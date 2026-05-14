from __future__ import annotations

import re
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

MAKYURA_THE_DESTRUCTOR = 0x14A5
CYBER_STEIN = 0x114A
MAGICAL_SCIENTIST = 0x1619
BRIONAC_DRAGON_OF_THE_ICE_BARRIER = 0x1D7C
MIND_MASTER = 0x1E22
PREMATURE_BURIAL = 0x1366
RING_OF_DESTRUCTION = 0x138D

HEAVY_STORM = 0x131B
MYSTICAL_SPACE_TYPHOON = 0x132D
MIRROR_FORCE = 0x1317
TORRENTIAL_TRIBUTE = 0x13FA
DARK_HOLE = 0x10F6
MAX_MAIN_DECK_SIZE = 60
YDC_HEADER_SIZE = 8

PLAYER_START_DECK_FILES = {
    # The player's opening decks; do not apply CPU deck power-card injections here.
    "rpg001_0_syoki.ydc",
    "rpg002_0_rd.ydc",
}

CPU_DECK_NAME_PATTERN = re.compile(r"(?:rpg|wcs|wrd)\d{3}")
TRUNCATED_RPG_DECK_NAME_PATTERN = re.compile(r"pg\d{3}")

CPU_DECK_REQUIRED_CARDS = (
    ("Mirror Force", MIRROR_FORCE),
    ("Torrential Tribute", TORRENTIAL_TRIBUTE),
    ("Dark Hole", DARK_HOLE),
    ("Ring of Destruction", RING_OF_DESTRUCTION),
)

CYBER_STEIN_HALF_LP_COST_HOOK = 0x021E4A20
CYBER_STEIN_HALF_LP_COST_CAVE = 0x0226CBBC
CYBER_STEIN_SUMMON_POSITION_PATCH = 0x0220B0B6
CYBER_STEIN_OPT_MARK_SUMMON_HOOK = 0x0220B0A0
CYBER_STEIN_OPT_MARK_SUMMON_CAVE = 0x0226C8A6
MAGICAL_SCIENTIST_OPT_MARK_SUMMON_HOOK = 0x02213226
MAGICAL_SCIENTIST_OPT_MARK_SUMMON_CAVE = 0x0226C8C2
CYBER_SCIENTIST_OPT_CHECK_CAVE = 0x0226CB96
MIND_BRIONAC_OPT_CHECK_CAVE = 0x0226C924
MIND_BRIONAC_OPT_MARK_RESOLVE_CAVE = 0x02294180
DECK_EDITOR_NORMALIZE_CARD_COUNT_CAVE = 0x02172FE8
CARD_COUNT_GETTER = 0x0202AFF8

CYBER_STEIN_EFFECT_CHECK_POINTER = 0x0227A2F8
CYBER_STEIN_EFFECT_RESOLVE_POINTER = 0x0227A2FC
MAGICAL_SCIENTIST_EFFECT_CHECK_POINTER = 0x0227AB38
BRIONAC_EFFECT_CHECK_POINTER = 0x0227C248
BRIONAC_EFFECT_RESOLVE_POINTER = 0x0227C24C
MIND_MASTER_EFFECT_CHECK_POINTER = 0x0227C530
MIND_MASTER_EFFECT_RESOLVE_POINTER = 0x0227C534

COMMON_FUSION_SUMMON_EFFECT_CHECK = 0x021F04AD
BRIONAC_EFFECT_CHECK = 0x021F03DD
BRIONAC_EFFECT_RESOLVE = 0x021EB5B9
MIND_MASTER_EFFECT_CHECK = 0x021F7A71
MIND_MASTER_EFFECT_RESOLVE = 0x021EB851

CYBER_STEIN_OLD_DESCRIPTION = (
    b"Pay 5000 Life Points. Special Summon 1 Fusion Monster from your Extra Deck to the field in Attack Position."
)
CYBER_STEIN_NEW_DESCRIPTION = (
    b"Once per turn: Pay half your LP. Special Summon 1 Fusion Monster from Extra Deck in open Defense Position. "
)

MAGICAL_SCIENTIST_OLD_DESCRIPTION = (
    b"Pay 1000 Life Points to Special Summon 1 level 6 or lower Fusion Monster from your Extra Deck in face-up "
    b"Attack or Defense Position. That Fusion Monster cannot attack your opponent's Life Points directly, and is "
    b"returned to your Extra Deck at the end of the turn."
)
MAGICAL_SCIENTIST_NEW_DESCRIPTION = (
    b"Once per turn: You can pay 1000 Life Points to Special Summon 1 Level 6 or lower Fusion Monster from your "
    b"Extra Deck in face-up Attack or Defense Position. That Fusion Monster cannot attack directly, and it is "
    b"returned to your Extra Deck at the end of this turn. "
)

MIND_MASTER_OLD_DESCRIPTION = (
    b"You can pay 800 Life Points and Tribute 1 Psychic-Type monster, except \"Mind Master\", to Special Summon "
    b"1 Level 4 or lower Psychic-Type monster from your Deck in face-up Attack Position."
)
MIND_MASTER_NEW_DESCRIPTION = (
    b"Once per turn: Pay 800 Life Points and Tribute 1 Psychic-Type monster, except \"Mind Master\", to Special "
    b"Summon 1 Level 4 or lower Psychic-Type monster from your Deck in Attack Position. "
)

BRIONAC_OLD_DESCRIPTION = (
    b"1 Tuner + 1 or more non-Tuner monsters\r\n"
    b"You can discard any number of cards to the Graveyard, to return the same number of cards from the field to "
    b"the hand."
)
BRIONAC_NEW_DESCRIPTION = (
    b"1 Tuner + 1 or more non-Tuner monsters\r\n"
    b"Once per turn: Discard any number of cards to the Graveyard, then return that many cards from the field to "
    b"the hand."
)

RING_OF_DESTRUCTION_OLD_DESCRIPTION = (
    b"Select and destroy 1 face-up monster, and inflict damage to both players equal to its ATK."
)
RING_OF_DESTRUCTION_NEW_DESCRIPTION = (
    b"Select and destroy 1 face-up monster. Opponent gains LP equal to its ATK; you take damage."
)


def thumb_bl(source_address: int, target_address: int) -> bytes:
    offset = target_address - (source_address + 4)
    if offset % 2:
        raise ValueError(f"Thumb BL target {target_address:#010x} is not halfword-aligned.")
    if offset < -(1 << 22) or offset >= (1 << 22):
        raise ValueError(f"Thumb BL target {target_address:#010x} is out of range from {source_address:#010x}.")

    immediate = (offset >> 1) & 0x3FFFFF
    high_halfword = 0xF000 | ((immediate >> 11) & 0x7FF)
    low_halfword = 0xF800 | (immediate & 0x7FF)
    return high_halfword.to_bytes(2, "little") + low_halfword.to_bytes(2, "little")


def arm_bl(source_address: int, target_address: int) -> bytes:
    offset = target_address - (source_address + 8)
    if offset % 4:
        raise ValueError(f"ARM BL target {target_address:#010x} is not word-aligned.")
    if offset < -(1 << 25) or offset >= (1 << 25):
        raise ValueError(f"ARM BL target {target_address:#010x} is out of range from {source_address:#010x}.")

    immediate = (offset >> 2) & 0xFFFFFF
    return (0xEB000000 | immediate).to_bytes(4, "little")


def arm_blx(source_address: int, target_address: int) -> bytes:
    offset = target_address - (source_address + 8)
    if offset % 2:
        raise ValueError(f"ARM BLX target {target_address:#010x} is not halfword-aligned.")
    if offset < -(1 << 25) or offset >= (1 << 25):
        raise ValueError(f"ARM BLX target {target_address:#010x} is out of range from {source_address:#010x}.")

    h = (offset >> 1) & 1
    immediate = (offset >> 2) & 0xFFFFFF
    return (0xFA000000 | (h << 24) | immediate).to_bytes(4, "little")


CYBER_STEIN_HALF_LP_COST_CAVE_BYTES = bytes.fromhex(
    """
    28 88 03 49 88 42 01 d1 02 49 08 47 02 49 70 47
    4a 11 00 00 15 4c 1e 02 a0 f2 26 02
    """
)

CYBER_SCIENTIST_OPT_CHECK_CAVE_BYTES = bytes.fromhex(
    """
    16 b4 04 1c 21 8b 05 4a 52 6b 01 32 91 42 02 d1
    00 20 16 bc 70 47 02 4b 20 1c 16 bc 18 47 7c ac
    29 02 ad 04 1f 02
    """
)

MIND_BRIONAC_OPT_CHECK_CAVE_BYTES = bytes.fromhex(
    """
    16 b4 04 1c 21 8b 09 4a 52 6b 01 32 91 42 02 d1
    00 20 16 bc 70 47 20 88 05 4b 98 42 01 d0 05 4b
    00 e0 05 4b 20 1c 16 bc 18 47 00 00 7c ac 29 02
    22 1e 00 00 dd 03 1f 02 71 7a 1f 02
    """
)

MIND_BRIONAC_OPT_MARK_RESOLVE_CAVE_BYTES = bytes.fromhex(
    """
    16 b4 04 1c 06 49 49 6b 01 31 21 83 20 88 05 4b
    98 42 01 d0 04 4b 00 e0 04 4b 20 1c 16 bc 18 47
    7c ac 29 02 22 1e 00 00 b9 b5 1e 02 51 b8 1e 02
    """
)

CYBER_STEIN_OPT_MARK_SUMMON_CAVE_BYTES = bytes.fromhex(
    """
    06 b4 03 49 49 6b 01 31 21 83 06 bc 25 88 01 48
    70 47 7c ac 29 02 42 0e 00 00
    """
)

MAGICAL_SCIENTIST_OPT_MARK_SUMMON_CAVE_BYTES = bytes.fromhex(
    """
    06 b4 03 49 49 6b 01 31 21 83 06 bc 21 88 01 48
    70 47 7c ac 29 02 81 14 00 00
    """
)

DECK_EDITOR_NORMALIZE_CARD_COUNT_CAVE_BYTES = (
    bytes.fromhex("04 e0 2d e5")
    + arm_blx(DECK_EDITOR_NORMALIZE_CARD_COUNT_CAVE + 4, CARD_COUNT_GETTER)
    + bytes.fromhex(
        """
        00 00 50 e3 03 00 a0 13 00 80 bd e8
        """
    )
)

CARD_STAT_CHANGES = [
    ("Makyura the Destructor", MAKYURA_THE_DESTRUCTOR, 0x28, 0x3C, 0x2F, 0x5F),
]

ARM9_OVERLAY_PATCHES = {
    8: [
        (
            0x021544A0,
            arm_blx(0x021544A0, CARD_COUNT_GETTER),
            arm_bl(0x021544A0, DECK_EDITOR_NORMALIZE_CARD_COUNT_CAVE),
        ),
        (
            0x021545D4,
            arm_blx(0x021545D4, CARD_COUNT_GETTER),
            arm_bl(0x021545D4, DECK_EDITOR_NORMALIZE_CARD_COUNT_CAVE),
        ),
        (
            0x021546B4,
            arm_blx(0x021546B4, CARD_COUNT_GETTER),
            arm_bl(0x021546B4, DECK_EDITOR_NORMALIZE_CARD_COUNT_CAVE),
        ),
        (
            0x02166470,
            arm_blx(0x02166470, CARD_COUNT_GETTER),
            arm_bl(0x02166470, DECK_EDITOR_NORMALIZE_CARD_COUNT_CAVE),
        ),
        (
            DECK_EDITOR_NORMALIZE_CARD_COUNT_CAVE,
            bytes(len(DECK_EDITOR_NORMALIZE_CARD_COUNT_CAVE_BYTES)),
            DECK_EDITOR_NORMALIZE_CARD_COUNT_CAVE_BYTES,
        ),
    ],
    3: [
        (
            0x02210662,
            bytes.fromhex("bf f7 2d fb"),  # bl 0x021CFCC0: damage opponent
            bytes.fromhex("c0 f7 8d f9"),  # bl 0x021D0980: heal opponent
        ),
        (
            CYBER_STEIN_HALF_LP_COST_HOOK,
            bytes.fromhex("28 88 89 49"),  # ldrh r0, [r5]; ldr r1, =0x0226F2A0
            thumb_bl(CYBER_STEIN_HALF_LP_COST_HOOK, CYBER_STEIN_HALF_LP_COST_CAVE),
        ),
        (
            CYBER_STEIN_OPT_MARK_SUMMON_HOOK,
            bytes.fromhex("25 88 1c 48"),  # ldrh r5, [r4]; ldr r0, =0x00000E42
            thumb_bl(CYBER_STEIN_OPT_MARK_SUMMON_HOOK, CYBER_STEIN_OPT_MARK_SUMMON_CAVE),
        ),
        (
            CYBER_STEIN_SUMMON_POSITION_PATCH,
            bytes.fromhex("00 26"),  # movs r6, #0: Attack Position
            bytes.fromhex("01 26"),  # movs r6, #1: face-up Defense Position
        ),
        (
            MAGICAL_SCIENTIST_OPT_MARK_SUMMON_HOOK,
            bytes.fromhex("21 88 0f 48"),  # ldrh r1, [r4]; ldr r0, =0x00001481
            thumb_bl(MAGICAL_SCIENTIST_OPT_MARK_SUMMON_HOOK, MAGICAL_SCIENTIST_OPT_MARK_SUMMON_CAVE),
        ),
        (
            CYBER_STEIN_EFFECT_CHECK_POINTER,
            COMMON_FUSION_SUMMON_EFFECT_CHECK.to_bytes(4, "little"),
            (CYBER_SCIENTIST_OPT_CHECK_CAVE | 1).to_bytes(4, "little"),
        ),
        (
            MAGICAL_SCIENTIST_EFFECT_CHECK_POINTER,
            COMMON_FUSION_SUMMON_EFFECT_CHECK.to_bytes(4, "little"),
            (CYBER_SCIENTIST_OPT_CHECK_CAVE | 1).to_bytes(4, "little"),
        ),
        (
            BRIONAC_EFFECT_CHECK_POINTER,
            BRIONAC_EFFECT_CHECK.to_bytes(4, "little"),
            (MIND_BRIONAC_OPT_CHECK_CAVE | 1).to_bytes(4, "little"),
        ),
        (
            BRIONAC_EFFECT_RESOLVE_POINTER,
            BRIONAC_EFFECT_RESOLVE.to_bytes(4, "little"),
            (MIND_BRIONAC_OPT_MARK_RESOLVE_CAVE | 1).to_bytes(4, "little"),
        ),
        (
            MIND_MASTER_EFFECT_CHECK_POINTER,
            MIND_MASTER_EFFECT_CHECK.to_bytes(4, "little"),
            (MIND_BRIONAC_OPT_CHECK_CAVE | 1).to_bytes(4, "little"),
        ),
        (
            MIND_MASTER_EFFECT_RESOLVE_POINTER,
            MIND_MASTER_EFFECT_RESOLVE.to_bytes(4, "little"),
            (MIND_BRIONAC_OPT_MARK_RESOLVE_CAVE | 1).to_bytes(4, "little"),
        ),
        (
            CYBER_SCIENTIST_OPT_CHECK_CAVE,
            bytes(len(CYBER_SCIENTIST_OPT_CHECK_CAVE_BYTES)),
            CYBER_SCIENTIST_OPT_CHECK_CAVE_BYTES,
        ),
        (
            CYBER_STEIN_HALF_LP_COST_CAVE,
            bytes(len(CYBER_STEIN_HALF_LP_COST_CAVE_BYTES)),
            CYBER_STEIN_HALF_LP_COST_CAVE_BYTES,
        ),
        (
            MIND_BRIONAC_OPT_CHECK_CAVE,
            bytes(len(MIND_BRIONAC_OPT_CHECK_CAVE_BYTES)),
            MIND_BRIONAC_OPT_CHECK_CAVE_BYTES,
        ),
        (
            MIND_BRIONAC_OPT_MARK_RESOLVE_CAVE,
            bytes(len(MIND_BRIONAC_OPT_MARK_RESOLVE_CAVE_BYTES)),
            MIND_BRIONAC_OPT_MARK_RESOLVE_CAVE_BYTES,
        ),
        (
            CYBER_STEIN_OPT_MARK_SUMMON_CAVE,
            bytes(len(CYBER_STEIN_OPT_MARK_SUMMON_CAVE_BYTES)),
            CYBER_STEIN_OPT_MARK_SUMMON_CAVE_BYTES,
        ),
        (
            MAGICAL_SCIENTIST_OPT_MARK_SUMMON_CAVE,
            bytes(len(MAGICAL_SCIENTIST_OPT_MARK_SUMMON_CAVE_BYTES)),
            MAGICAL_SCIENTIST_OPT_MARK_SUMMON_CAVE_BYTES,
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
    ("Black Luster Soldier - Envoy of the Beginning", 0x16CB, FORBIDDEN),
    ("Cold Wave", 0x1407, FORBIDDEN),
    ("Gravity Bind", 0x140E, FORBIDDEN),
    ("Symbol of Heritage", 0x19D7, FORBIDDEN),
    ("Ojama Trio", 0x166A, FORBIDDEN),
    ("Chain Strike", 0x1AF8, FORBIDDEN),
    ("Wall of Revealing Light", 0x1766, FORBIDDEN),
    ("Royal Oppression", 0x1517, FORBIDDEN),
    ("Monster Reborn", 0x12EA, FORBIDDEN),
    ("Level Limit - Area B", 0x17A6, FORBIDDEN),
    ("Final Countdown", 0x169C, FORBIDDEN),
    ("Gateway of the Six", 0x219A, FORBIDDEN),
    ("Trap Dustshoot", 0x1546, FORBIDDEN),
    ("Royal Tribute", 0x15A4, LIMITED),
    ("Cyber-Stein", CYBER_STEIN, LIMITED),
    ("Magical Scientist", MAGICAL_SCIENTIST, LIMITED),
    ("Premature Burial", PREMATURE_BURIAL, LIMITED),
    ("Deck Devastation Virus", 0x188C, LIMITED),
    ("Metamorphosis", 0x15A3, LIMITED),
    ("Dark Magician of Chaos", 0x16F8, LIMITED),
    ("Substitoad", 0x1DB1, LIMITED),
    ("Sinister Serpent", 0x1181, LIMITED),
    ("Rescue Cat", 0x1876, LIMITED),
    ("Dark Strike Fighter", 0x1F63, LIMITED),
    ("Dark Armed Dragon", 0x1CFD, LIMITED),
    ("Last Will", 0x1315, LIMITED),
    ("Ring of Destruction", RING_OF_DESTRUCTION, LIMITED),
    ("Honest", 0x1D96, LIMITED),
    ("Morphing Jar #2", 0x1369, LIMITED),
    ("Spirit Reaper", 0x1596, LIMITED),
    ("Neo-Spacian Grand Mole", 0x1A72, LIMITED),
    ("Blackwing - Kalut the Moon Shadow", 0x1FE4, LIMITED),
    ("Mystical Space Typhoon", 0x132D, LIMITED),
    ("Magic Cylinder", 0x1404, LIMITED),
    ("Gladiator Beast War Chariot", 0x1E53, LIMITED),
    ("Skill Drain", 0x166C, LIMITED),
    ("Shien's Smoke Signal", 0x247B, LIMITED),
    ("Magician of Faith", 0x1152, SEMI_LIMITED),
    ("Tribe-Infecting Virus", 0x161C, SEMI_LIMITED),
    ("Card Trooper", 0x1B1B, SEMI_LIMITED),
    ("Eradicator Epidemic Virus", 0x1BF1, SEMI_LIMITED),
    ("Gladiator Beast Bestiari", 0x1C75, SEMI_LIMITED),
    ("Dimensional Fissure", 0x1A33, SEMI_LIMITED),
    ("Lumina, Lightsworn Summoner", 0x1DAA, SEMI_LIMITED),
    ("Macro Cosmos", 0x1A1A, SEMI_LIMITED),
    ("Mezuki", 0x1CBF, SEMI_LIMITED),
    ("Necro Gardna", 0x1C0A, SEMI_LIMITED),
    ("Necroface", 0x17BB, SEMI_LIMITED),
    ("Burial from a Different Dimension", 0x1B1D, SEMI_LIMITED),
    ("One for One", 0x2005, SEMI_LIMITED),
    ("Megamorph", 0x1237, SEMI_LIMITED),
    ("Reasoning", 0x159A, SEMI_LIMITED),
    ("Scapegoat", 0x12D2, SEMI_LIMITED),
    ("Book of Moon", 0x1538, SEMI_LIMITED),
    ("Advanced Ritual Art", 0x1B54, SEMI_LIMITED),
    ("Foolish Burial", 0x1474, SEMI_LIMITED),
    ("Debris Dragon", 0x1F45, SEMI_LIMITED),
    ("Tsukuyomi", 0x1694, SEMI_LIMITED),
    ("Night Assailant", 0x179A, SEMI_LIMITED),
    ("Emergency Teleport", 0x1E43, SEMI_LIMITED),
    ("Sangan", 0x0FD6, SEMI_LIMITED),
    ("Return from the Different Dimension", 0x17BE, SEMI_LIMITED),
    ("Chaos Sorcerer", 0x16C9, UNLIMITED),
    ("Left Arm of the Forbidden One", 0x0FBA, UNLIMITED),
    ("Left Leg of the Forbidden One", 0x0FB8, UNLIMITED),
    ("Temple of the Kings", 0x146F, UNLIMITED),
    ("Time Seal", 0x1378, UNLIMITED),
    ("Monster Gate", 0x175C, UNLIMITED),
    ("Right Arm of the Forbidden One", 0x0FB9, UNLIMITED),
    ("Right Leg of the Forbidden One", 0x0FB7, UNLIMITED),
    ("Snipe Hunter", 0x1ADF, UNLIMITED),
    ("Ultimate Offering", 0x12F3, UNLIMITED),
    ("Magical Stone Excavation", 0x1638, UNLIMITED),
    ("Dewloren, Tiger King of the Ice Barrier", 0x1F22, UNLIMITED),
    ("Gold Sarcophagus", 0x1811, UNLIMITED),
    ("Makyura the Destructor", MAKYURA_THE_DESTRUCTOR, UNLIMITED),
    ("Mind Master", MIND_MASTER, UNLIMITED),
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


def replace_unique(data: bytearray, old_value: bytes, new_value: bytes, label: str) -> None:
    position = data.find(old_value)
    if position < 0:
        raise ValueError(f"Could not find {label}.")
    if data.find(old_value, position + 1) >= 0:
        raise ValueError(f"Found more than one {label}.")
    if len(new_value) != len(old_value):
        raise ValueError(f"{label} replacement must stay the same length.")

    data[position : position + len(old_value)] = new_value


def patch_card_desc_e(desc_data: bytearray) -> None:
    replace_unique(
        desc_data,
        RING_OF_DESTRUCTION_OLD_DESCRIPTION,
        RING_OF_DESTRUCTION_NEW_DESCRIPTION,
        "Ring of Destruction English description",
    )
    replace_unique(
        desc_data,
        CYBER_STEIN_OLD_DESCRIPTION,
        CYBER_STEIN_NEW_DESCRIPTION,
        "Cyber-Stein English description",
    )
    replace_unique(
        desc_data,
        MAGICAL_SCIENTIST_OLD_DESCRIPTION,
        MAGICAL_SCIENTIST_NEW_DESCRIPTION,
        "Magical Scientist English description",
    )
    replace_unique(
        desc_data,
        MIND_MASTER_OLD_DESCRIPTION,
        MIND_MASTER_NEW_DESCRIPTION,
        "Mind Master English description",
    )
    replace_unique(
        desc_data,
        BRIONAC_OLD_DESCRIPTION,
        BRIONAC_NEW_DESCRIPTION,
        "Brionac, Dragon of the Ice Barrier English description",
    )


def patch_card_prop(card_prop_data: bytearray) -> None:
    if len(card_prop_data) % 8 != 0:
        raise ValueError(f"Unexpected card_prop.bin size: {len(card_prop_data)} bytes.")

    for name, code, expected_attack_byte, expected_defense_byte, attack_byte, defense_byte in CARD_STAT_CHANGES:
        matches = []
        for offset in range(0, len(card_prop_data), 8):
            card_code = int.from_bytes(card_prop_data[offset : offset + 2], "little") & 0x3FFF
            if card_code == code:
                matches.append(offset)

        if len(matches) != 1:
            raise ValueError(f"Expected one {name} card_prop.bin row, found {len(matches)}.")

        offset = matches[0]
        actual_attack_byte = card_prop_data[offset + 2]
        actual_defense_byte = card_prop_data[offset + 3]
        if (actual_attack_byte, actual_defense_byte) != (expected_attack_byte, expected_defense_byte):
            raise ValueError(
                f"{name} expected stat bytes {expected_attack_byte:02X} {expected_defense_byte:02X} "
                f"but found {actual_attack_byte:02X} {actual_defense_byte:02X}."
            )

        card_prop_data[offset + 2] = attack_byte
        card_prop_data[offset + 3] = defense_byte


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


def patch_cpu_deck_cards(deck_data: bytearray, deck_name: str) -> None:
    if not is_cpu_deck_file(deck_name):
        return

    main_count_offset = YDC_HEADER_SIZE
    main_count = read_u16(deck_data, main_count_offset, deck_name, "main deck count")
    main_start = main_count_offset + 2
    main_end = main_start + (main_count * 2)
    validate_ydc_sections(deck_data, deck_name)

    main_cards = [
        read_u16(deck_data, main_start + (i * 2), deck_name, f"main deck card {i}")
        for i in range(main_count)
    ]

    def append_main_deck_card(card_name: str, card_code: int) -> None:
        nonlocal main_count, main_end
        if main_count >= MAX_MAIN_DECK_SIZE:
            raise ValueError(
                f"{deck_name} cannot add {card_name} because its main deck already has {main_count} cards."
            )

        deck_data[main_count_offset : main_count_offset + 2] = (main_count + 1).to_bytes(2, "little")
        deck_data[main_end:main_end] = card_code.to_bytes(2, "little")
        main_cards.append(card_code)
        main_count += 1
        main_end += 2

    if HEAVY_STORM not in main_cards:
        mystical_space_typhoons = [
            index
            for index, card in enumerate(main_cards)
            if card == MYSTICAL_SPACE_TYPHOON
        ]
        if len(mystical_space_typhoons) >= 2:
            replacement_index = mystical_space_typhoons[-1]
            replacement_offset = main_start + (replacement_index * 2)
            deck_data[replacement_offset : replacement_offset + 2] = HEAVY_STORM.to_bytes(2, "little")
            main_cards[replacement_index] = HEAVY_STORM
        else:
            append_main_deck_card("Heavy Storm", HEAVY_STORM)

    for card_name, card_code in CPU_DECK_REQUIRED_CARDS:
        if card_code not in main_cards:
            append_main_deck_card(card_name, card_code)


def is_cpu_deck_file(deck_name: str) -> bool:
    normalized = deck_name.casefold()
    if normalized in PLAYER_START_DECK_FILES:
        return False

    return bool(
        CPU_DECK_NAME_PATTERN.search(normalized)
        or TRUNCATED_RPG_DECK_NAME_PATTERN.match(normalized)
    )


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
    patch_nested_file(rom, 51, "card_prop.bin", patch_card_prop)
    patched_decks = patch_nested_files(rom, DECK_PAC_ROM_FILE_ID, patch_cpu_deck_cards)
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
