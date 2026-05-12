from __future__ import annotations

from pathlib import Path

import ndspy.code
import ndspy.rom


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROM = REPO_ROOT / "build" / "YGO2011-Nexus-Revival-0.5.nds"
OUTPUT_ROM = REPO_ROOT / "build" / "YGO2011-Quality-Nexus.nds"

OLD_LIST_NAME = b"List - September, 2010"
NEW_LIST_NAME = b"Quality List - 2010"

LIMIT_FILE = "limit201009.bin"
DECK_PAC_ROM_FILE_ID = 61

RING_OF_DESTRUCTION = 0x138D

HEAVY_STORM = 0x131B
MYSTICAL_SPACE_TYPHOON = 0x132D
MAX_MAIN_DECK_SIZE = 60
YDC_HEADER_SIZE = 8

RING_OF_DESTRUCTION_OLD_DESCRIPTION = (
    b"Select and destroy 1 face-up monster, and inflict damage to both players equal to its ATK."
)
RING_OF_DESTRUCTION_NEW_DESCRIPTION = (
    b"Select and destroy 1 face-up monster. Opponent gains LP equal to its ATK; you take damage."
)

ARM9_OVERLAY_PATCHES = {
    3: [
        (
            0x02210662,
            bytes.fromhex("bf f7 2d fb"),  # bl 0x021CFCC0: damage opponent
            bytes.fromhex("c0 f7 8d f9"),  # bl 0x021D0980: heal opponent
        ),
    ],
}

FORBIDDEN = 0x0000
LIMITED = 0x4000
SEMI_LIMITED = 0x8000
UNLIMITED = None
STATUS_ORDER = (FORBIDDEN, LIMITED, SEMI_LIMITED)

LIMIT_CHANGES = [
    ("Heavy Storm", 0x131B, LIMITED),
    ("Exodia the Forbidden One", 0x0FBB, FORBIDDEN),
    ("Cold Wave", 0x1407, FORBIDDEN),
    ("Gravity Bind", 0x140E, FORBIDDEN),
    ("Symbol of Heritage", 0x19D7, FORBIDDEN),
    ("Ojama Trio", 0x166A, FORBIDDEN),
    ("Chain Strike", 0x1AF8, FORBIDDEN),
    ("Wall of Revealing Light", 0x1766, FORBIDDEN),
    ("Royal Oppression", 0x1517, FORBIDDEN),
    ("Monster Reborn", 0x12EA, FORBIDDEN),
    ("Level Limit - Area B", 0x17A6, FORBIDDEN),
    ("Gateway of the Six", 0x219A, FORBIDDEN),
    ("Royal Tribute", 0x15A4, LIMITED),
    ("Black Luster Soldier - Envoy of the Beginning", 0x16CB, LIMITED),
    ("Cyber-Stein", 0x114A, LIMITED),
    ("Metamorphosis", 0x15A3, LIMITED),
    ("Dark Magician of Chaos", 0x16F8, LIMITED),
    ("Substitoad", 0x1DB1, LIMITED),
    ("Sinister Serpent", 0x1181, LIMITED),
    ("Rescue Cat", 0x1876, LIMITED),
    ("Dark Strike Fighter", 0x1F63, LIMITED),
    ("Last Will", 0x1315, LIMITED),
    ("Ring of Destruction", RING_OF_DESTRUCTION, LIMITED),
    ("Temple of the Kings", 0x146F, LIMITED),
    ("Time Seal", 0x1378, LIMITED),
    ("Blackwing - Kalut the Moon Shadow", 0x1FE4, LIMITED),
    ("Mystical Space Typhoon", 0x132D, LIMITED),
    ("Magic Cylinder", 0x1404, LIMITED),
    ("Gladiator Beast War Chariot", 0x1E53, LIMITED),
    ("Skill Drain", 0x166C, LIMITED),
    ("Shien's Smoke Signal", 0x247B, LIMITED),
    ("Makyura the Destructor", 0x14A5, SEMI_LIMITED),
    ("Magician of Faith", 0x1152, SEMI_LIMITED),
    ("Tribe-Infecting Virus", 0x161C, SEMI_LIMITED),
    ("Card Trooper", 0x1B1B, SEMI_LIMITED),
    ("Dark Armed Dragon", 0x1CFD, SEMI_LIMITED),
    ("Gladiator Beast Bestiari", 0x1C75, SEMI_LIMITED),
    ("Lumina, Lightsworn Summoner", 0x1DAA, SEMI_LIMITED),
    ("Mezuki", 0x1CBF, SEMI_LIMITED),
    ("Necro Gardna", 0x1C0A, SEMI_LIMITED),
    ("Necroface", 0x17BB, SEMI_LIMITED),
    ("Spirit Reaper", 0x1596, SEMI_LIMITED),
    ("Burial from a Different Dimension", 0x1B1D, SEMI_LIMITED),
    ("One for One", 0x2005, SEMI_LIMITED),
    ("Megamorph", 0x1237, SEMI_LIMITED),
    ("Reasoning", 0x159A, SEMI_LIMITED),
    ("Scapegoat", 0x12D2, SEMI_LIMITED),
    ("Monster Gate", 0x175C, SEMI_LIMITED),
    ("Book of Moon", 0x1538, SEMI_LIMITED),
    ("Advanced Ritual Art", 0x1B54, SEMI_LIMITED),
    ("Foolish Burial", 0x1474, SEMI_LIMITED),
    ("Neo-Spacian Grand Mole", 0x1A72, SEMI_LIMITED),
    ("Debris Dragon", 0x1F45, SEMI_LIMITED),
    ("Tsukuyomi", 0x1694, SEMI_LIMITED),
    ("Night Assailant", 0x179A, SEMI_LIMITED),
    ("Emergency Teleport", 0x1E43, SEMI_LIMITED),
    ("Sangan", 0x0FD6, SEMI_LIMITED),
    ("Return from the Different Dimension", 0x17BE, SEMI_LIMITED),
    ("Tragoedia", 0x1F99, UNLIMITED),
    ("Allure of Darkness", 0x1D92, UNLIMITED),
    ("Destiny Draw", 0x1B26, UNLIMITED),
    ("Summoner Monk", 0x1900, UNLIMITED),
    ("The Transmigration Prophecy", 0x1B62, UNLIMITED),
    ("Lonefire Blossom", 0x1D90, UNLIMITED),
]


def parse_pac_entries(pac_data: bytes) -> dict[str, tuple[int, int]]:
    return {
        name: (entry["offset"], entry["size"])
        for name, entry in parse_pac_layout(pac_data).items()
    }


def parse_pac_layout(pac_data: bytes) -> dict[str, dict[str, int]]:
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
            entries.append(
                {
                    "offset": data_start + offset,
                    "size": size,
                    "table_offset": file_names_start + i,
                }
            )

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
    entries = parse_pac_layout(pac_data)
    entry = entries[nested_name]
    offset = entry["offset"]
    size = entry["size"]
    nested = bytearray(pac_data[offset : offset + size])
    patcher(nested)

    next_offsets = [
        other["offset"]
        for name, other in entries.items()
        if name != nested_name and other["offset"] > offset
    ]
    next_offset = min(next_offsets, default=len(pac_data))
    capacity = next_offset - offset
    if len(nested) > capacity:
        raise ValueError(
            f"{nested_name} grew from {size} to {len(nested)} bytes, "
            f"but only {capacity} bytes are available before the next PAC file."
        )

    pac_data[offset : offset + len(nested)] = nested
    if len(nested) < size:
        pac_data[offset + len(nested) : offset + size] = b"\x00" * (size - len(nested))
    pac_data[entry["table_offset"] + 4 : entry["table_offset"] + 8] = len(nested).to_bytes(4, "little")
    rom.files[rom_file_id] = bytes(pac_data)


def patch_nested_files(
    rom: ndspy.rom.NintendoDSRom,
    rom_file_id: int,
    patcher,
) -> int:
    pac_data = bytearray(rom.files[rom_file_id])
    entries = parse_pac_layout(pac_data)
    patched = 0

    for nested_name, entry in entries.items():
        offset = entry["offset"]
        size = entry["size"]
        nested = bytearray(pac_data[offset : offset + size])
        original = bytes(nested)
        patcher(nested, nested_name)
        if bytes(nested) == original:
            continue

        next_offsets = [
            other["offset"]
            for name, other in entries.items()
            if name != nested_name and other["offset"] > offset
        ]
        next_offset = min(next_offsets, default=len(pac_data))
        capacity = next_offset - offset
        if len(nested) > capacity:
            raise ValueError(
                f"{nested_name} grew from {size} to {len(nested)} bytes, "
                f"but only {capacity} bytes are available before the next PAC file."
            )

        pac_data[offset : offset + len(nested)] = nested
        if len(nested) < size:
            pac_data[offset + len(nested) : offset + size] = b"\x00" * (size - len(nested))
        pac_data[entry["table_offset"] + 4 : entry["table_offset"] + 8] = len(nested).to_bytes(4, "little")
        patched += 1

    rom.files[rom_file_id] = bytes(pac_data)
    return patched


def patch_limit_201009(limit_data: bytearray) -> None:
    values = [int.from_bytes(limit_data[i : i + 2], "little") for i in range(0, len(limit_data), 2)]
    header = values[:4]
    entries = values[4:]

    if header[0] != len(entries):
        raise ValueError(f"Unexpected {LIMIT_FILE} entry count header: {header[0]} vs {len(entries)}.")

    validate_limit_changes()
    change_by_code = {code: target_status for _name, code, target_status in LIMIT_CHANGES}
    original_by_code = {value & 0x3FFF: value for value in entries}

    missing_existing = [
        name
        for name, code, target_status in LIMIT_CHANGES
        if target_status is UNLIMITED and code not in original_by_code
    ]
    if missing_existing:
        raise ValueError(f"Cannot make already-unlisted cards unlimited: {missing_existing}.")

    sections = {status: [] for status in STATUS_ORDER}
    for value in entries:
        code = value & 0x3FFF
        if code in change_by_code:
            continue
        status = value & 0xC000
        sections[status].append(value)

    for _name, code, target_status in LIMIT_CHANGES:
        if target_status is not UNLIMITED:
            sections[target_status].append(code | target_status)

    entries = [value for status in STATUS_ORDER for value in sections[status]]
    header[0] = len(entries)

    updated_values = header + entries
    limit_data[:] = bytearray(len(updated_values) * 2)
    for i, value in enumerate(updated_values):
        limit_data[i * 2 : i * 2 + 2] = value.to_bytes(2, "little")


def validate_limit_changes() -> None:
    by_name = {}
    by_code = {}
    for name, code, target_status in LIMIT_CHANGES:
        normalized = name.casefold()
        if normalized in by_name and by_name[normalized] != target_status:
            raise ValueError(f"{name} has conflicting target statuses.")
        if code in by_code and by_code[code] != target_status:
            raise ValueError(f"{name} shares code {code:04X} with a conflicting target status.")
        by_name[normalized] = target_status
        by_code[code] = target_status


def patch_list_name(text_data: bytearray) -> None:
    position = text_data.find(OLD_LIST_NAME)
    if position < 0:
        raise ValueError(f"Could not find {OLD_LIST_NAME!r}.")
    if text_data.find(OLD_LIST_NAME, position + 1) >= 0:
        raise ValueError(f"Found more than one {OLD_LIST_NAME!r}.")

    replacement = NEW_LIST_NAME + (b"\x00" * (len(OLD_LIST_NAME) - len(NEW_LIST_NAME)))
    text_data[position : position + len(OLD_LIST_NAME)] = replacement


def patch_card_desc_e(desc_data: bytearray) -> None:
    position = desc_data.find(RING_OF_DESTRUCTION_OLD_DESCRIPTION)
    if position < 0:
        raise ValueError("Could not find Ring of Destruction's old English description.")
    if desc_data.find(RING_OF_DESTRUCTION_OLD_DESCRIPTION, position + 1) >= 0:
        raise ValueError("Found more than one Ring of Destruction English description.")
    if len(RING_OF_DESTRUCTION_NEW_DESCRIPTION) != len(RING_OF_DESTRUCTION_OLD_DESCRIPTION):
        raise ValueError("Ring of Destruction replacement description must stay the same length.")

    desc_data[position : position + len(RING_OF_DESTRUCTION_OLD_DESCRIPTION)] = (
        RING_OF_DESTRUCTION_NEW_DESCRIPTION
    )


def patch_arm9_overlay_bytes(rom: ndspy.rom.NintendoDSRom) -> None:
    overlays = rom.loadArm9Overlays()

    for overlay_id, patches in ARM9_OVERLAY_PATCHES.items():
        overlay = overlays[overlay_id]
        for ram_address, expected, replacement in patches:
            offset = ram_address - overlay.ramAddress
            if offset < 0 or offset + len(expected) > len(overlay.data):
                raise ValueError(f"Overlay {overlay_id} address {ram_address:#010x} is out of range.")
            actual = bytes(overlay.data[offset : offset + len(expected)])
            if actual != expected:
                raise ValueError(
                    f"Overlay {overlay_id} address {ram_address:#010x} expected "
                    f"{expected.hex(' ')} but found {actual.hex(' ')}."
                )
            overlay.data[offset : offset + len(expected)] = replacement

        rom.files[overlay.fileID] = overlay.save(compress=overlay.compressed)

    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(overlays)


def patch_cpu_deck_heavy_storm(deck_data: bytearray, deck_name: str) -> None:
    main_count_offset = YDC_HEADER_SIZE
    main_count = read_u16(deck_data, main_count_offset, deck_name, "main deck count")
    main_start = main_count_offset + 2
    main_end = main_start + (main_count * 2)
    validate_ydc_sections(deck_data, deck_name)

    main_cards = [
        read_u16(deck_data, main_start + (i * 2), deck_name, f"main deck card {i}")
        for i in range(main_count)
    ]
    if HEAVY_STORM in main_cards:
        return

    mystical_space_typhoons = [
        index
        for index, card in enumerate(main_cards)
        if card == MYSTICAL_SPACE_TYPHOON
    ]
    if len(mystical_space_typhoons) >= 2:
        replacement_offset = main_start + (mystical_space_typhoons[-1] * 2)
        deck_data[replacement_offset : replacement_offset + 2] = HEAVY_STORM.to_bytes(2, "little")
        return

    if main_count >= MAX_MAIN_DECK_SIZE:
        raise ValueError(f"{deck_name} cannot add Heavy Storm because its main deck already has {main_count} cards.")

    deck_data[main_count_offset : main_count_offset + 2] = (main_count + 1).to_bytes(2, "little")
    deck_data[main_end:main_end] = HEAVY_STORM.to_bytes(2, "little")


def validate_ydc_sections(deck_data: bytearray, deck_name: str) -> None:
    position = YDC_HEADER_SIZE
    main_count = read_u16(deck_data, position, deck_name, "main deck count")
    position += 2 + (main_count * 2)

    extra_count = read_u16(deck_data, position, deck_name, "extra deck count")
    position += 2 + (extra_count * 2)

    side_count = read_u16(deck_data, position, deck_name, "side deck count")
    position += 2 + (side_count * 2)

    if position != len(deck_data):
        raise ValueError(f"{deck_name} has {len(deck_data) - position} trailing bytes after its YDC deck sections.")


def read_u16(data: bytearray, offset: int, file_name: str, field_name: str) -> int:
    if offset + 2 > len(data):
        raise ValueError(f"{file_name} ended before {field_name}.")
    return int.from_bytes(data[offset : offset + 2], "little")


def main() -> None:
    if len(NEW_LIST_NAME) > len(OLD_LIST_NAME):
        raise ValueError("New list name must not be longer than the original in-place string.")
    if not SOURCE_ROM.exists():
        raise FileNotFoundError(f"Missing source ROM: {SOURCE_ROM}")

    rom = ndspy.rom.NintendoDSRom.fromFile(str(SOURCE_ROM))
    patch_arm9_overlay_bytes(rom)
    patch_nested_file(rom, 50, LIMIT_FILE, patch_limit_201009)
    patch_nested_file(rom, 51, "card_desc_e.bin", patch_card_desc_e)
    patched_decks = patch_nested_files(rom, DECK_PAC_ROM_FILE_ID, patch_cpu_deck_heavy_storm)
    patch_nested_file(rom, 51, "game_text_e.bin", patch_list_name)
    patch_nested_file(rom, 95, "system_txt_e.bin", patch_list_name)

    OUTPUT_ROM.parent.mkdir(parents=True, exist_ok=True)
    rom.saveToFile(str(OUTPUT_ROM))
    restore_trailing_padding(SOURCE_ROM, OUTPUT_ROM)
    print(f"Patched {patched_decks} CPU decks.")
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
