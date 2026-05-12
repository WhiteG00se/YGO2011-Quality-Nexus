from __future__ import annotations

from collections import Counter
from pathlib import Path

import ndspy.rom


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROM = REPO_ROOT / "build" / "YGO2011-Nexus-Revival-0.5.nds"
OUTPUT_ROM = REPO_ROOT / "build" / "YGO2011-Quality-Nexus.nds"

OLD_LIST_NAME = b"List - September, 2010"
NEW_LIST_NAME = b"Quality List - 2010"

LIMIT_FILE = "limit201009.bin"
HEAVY_STORM_FORBIDDEN = 0x131B
HEAVY_STORM_LIMITED = HEAVY_STORM_FORBIDDEN | 0x4000
HEAVY_STORM_FORBIDDEN_ENTRY_INDEX = 24
HEAVY_STORM_LIMITED_INSERT_INDEX = 76


def parse_pac_entries(pac_data: bytes) -> dict[str, tuple[int, int]]:
    line_break_bytes = set(range(0x0A, 0x19))
    header = file_names_start = file_names = third = data_start = None

    for i in range(len(pac_data) - 1):
        if i % 2 == 0 and pac_data[i] == 0xFF and pac_data[i + 1] == 0xFF:
            header_end = i - (i % 16)
            header = pac_data[:header_end]
            file_names_start = header_end
            break
    if header is None or file_names_start is None:
        raise ValueError("Could not find PAC header boundary.")

    for i in range(file_names_start, len(pac_data) - 7):
        if i % 16 == file_names_start % 16 and int.from_bytes(pac_data[i : i + 8], "little") == 0:
            file_names = pac_data[file_names_start:i]
            third = i
            break
    if file_names is None or third is None:
        raise ValueError("Could not find PAC file table boundary.")

    for i in range(third, len(pac_data) - 7):
        if i % 16 == third % 16 and int.from_bytes(pac_data[i : i + 8], "little") != 0:
            data_start = i
            break
    if data_start is None:
        raise ValueError("Could not find PAC data boundary.")

    raw_names = []
    start = 0
    skip_next = False
    for i, byte in enumerate(header):
        if skip_next:
            skip_next = False
            continue
        if byte in line_break_bytes:
            raw_names.append(header[start:i])
            start = i + 2
            skip_next = True

    final = len(header) - 1
    while final >= 3 and header[final - 3] == 0:
        final -= 1
    raw_names.append(header[start:final])

    names = [
        raw_name.decode("utf-8", errors="replace").split("\x00", 1)[0]
        for raw_name in raw_names
        if b"." in raw_name
    ]

    entries = []
    for i in range(8, len(file_names), 8):
        if i + 8 > len(file_names):
            continue
        offset = int.from_bytes(file_names[i : i + 4], "little")
        size = int.from_bytes(file_names[i + 4 : i + 8], "little")
        if size:
            entries.append((data_start + offset, size))

    if len(names) != len(entries):
        raise ValueError(f"PAC name/entry mismatch: {len(names)} names, {len(entries)} entries.")

    return dict(zip(names, entries))


def patch_nested_file(
    rom: ndspy.rom.NintendoDSRom,
    rom_file_id: int,
    nested_name: str,
    patcher,
) -> None:
    pac_data = bytearray(rom.files[rom_file_id])
    entries = parse_pac_entries(pac_data)
    offset, size = entries[nested_name]
    nested = bytearray(pac_data[offset : offset + size])
    patcher(nested)
    if len(nested) != size:
        raise ValueError(f"{nested_name} changed size from {size} to {len(nested)}.")
    pac_data[offset : offset + size] = nested
    rom.files[rom_file_id] = bytes(pac_data)


def patch_limit_201009(limit_data: bytearray) -> None:
    values = [int.from_bytes(limit_data[i : i + 2], "little") for i in range(0, len(limit_data), 2)]
    header = values[:4]
    entries = values[4:]

    if header[0] != len(entries):
        raise ValueError(f"Unexpected {LIMIT_FILE} entry count header: {header[0]} vs {len(entries)}.")
    if entries[HEAVY_STORM_FORBIDDEN_ENTRY_INDEX] != HEAVY_STORM_FORBIDDEN:
        found = [i for i, value in enumerate(entries) if value == HEAVY_STORM_FORBIDDEN]
        raise ValueError(f"Heavy Storm forbidden entry not at expected index; found {found}.")
    if HEAVY_STORM_LIMITED in entries:
        raise ValueError("Heavy Storm is already limited in this list.")

    entries.pop(HEAVY_STORM_FORBIDDEN_ENTRY_INDEX)
    entries.insert(HEAVY_STORM_LIMITED_INSERT_INDEX - 1, HEAVY_STORM_LIMITED)

    status_counts = Counter(value & 0xC000 for value in entries)
    expected_counts = Counter({0x0000: 46, 0x4000: 68, 0x8000: 18})
    if status_counts != expected_counts:
        raise ValueError(f"Unexpected limit status counts: {status_counts}.")

    updated_values = header + entries
    for i, value in enumerate(updated_values):
        limit_data[i * 2 : i * 2 + 2] = value.to_bytes(2, "little")


def patch_list_name(text_data: bytearray) -> None:
    position = text_data.find(OLD_LIST_NAME)
    if position < 0:
        raise ValueError(f"Could not find {OLD_LIST_NAME!r}.")
    if text_data.find(OLD_LIST_NAME, position + 1) >= 0:
        raise ValueError(f"Found more than one {OLD_LIST_NAME!r}.")

    replacement = NEW_LIST_NAME + (b"\x00" * (len(OLD_LIST_NAME) - len(NEW_LIST_NAME)))
    text_data[position : position + len(OLD_LIST_NAME)] = replacement


def main() -> None:
    if len(NEW_LIST_NAME) > len(OLD_LIST_NAME):
        raise ValueError("New list name must not be longer than the original in-place string.")
    if not SOURCE_ROM.exists():
        raise FileNotFoundError(f"Missing source ROM: {SOURCE_ROM}")

    rom = ndspy.rom.NintendoDSRom.fromFile(str(SOURCE_ROM))
    patch_nested_file(rom, 50, LIMIT_FILE, patch_limit_201009)
    patch_nested_file(rom, 51, "game_text_e.bin", patch_list_name)
    patch_nested_file(rom, 95, "system_txt_e.bin", patch_list_name)

    OUTPUT_ROM.parent.mkdir(parents=True, exist_ok=True)
    rom.saveToFile(str(OUTPUT_ROM))
    restore_trailing_padding(SOURCE_ROM, OUTPUT_ROM)
    print(f"Wrote {OUTPUT_ROM.relative_to(REPO_ROOT)}")


def restore_trailing_padding(source_rom: Path, output_rom: Path) -> None:
    source_size = source_rom.stat().st_size
    output_size = output_rom.stat().st_size
    if output_size > source_size:
        raise ValueError(f"Output ROM is larger than source ROM: {output_size} > {source_size}.")
    if output_size == source_size:
        return

    with source_rom.open("rb") as source:
        source.seek(output_size)
        padding = source.read()
    with output_rom.open("ab") as output:
        output.write(padding)


if __name__ == "__main__":
    main()
