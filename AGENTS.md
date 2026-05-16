# AGENTS.md

Guidance for coding agents working on this repo.

## Project

This repo builds an xdelta mod patch for `Yu-Gi-Oh! 5D's World Championship 2011: Over the Nexus`.

The tested base is the US English ROM:

- `YGO2011-Over_The_Nexus_USA_unpatched.nds`
- SHA256: `394A146733D118E0A685D5615213125D5A94FE72F05A3F9F988FA1418EFB5709`

Patch chain:

1. Apply `YGO.Nexus.Revival.0.5.xdelta` to the clean base ROM.
2. Run this repo's Python patcher against the Revival ROM.
3. Encode the difference from the Revival ROM as `Quality_Patch.xdelta`.
4. Validate that `Quality_Patch.xdelta` recreates the generated Quality ROM.

## Important files

- `README.md`: user install instructions, feature summary, and short development entry point.
- `scripts\apply-revival-patch.ps1`: applies Nexus Revival and checks fixed hashes.
- `scripts\apply-quality-patch.py`: modifies the Revival ROM into the Quality ROM.
- `scripts\create-xdelta-as-diff.ps1`: builds the Quality ROM, recreates `Quality_Patch.xdelta`, and validates it.
- `scripts\validate-xdelta.ps1`: verifies `Quality_Patch.xdelta` against the generated Quality ROM.

## Requirements

`requirements.txt` only lists Python packages. The full local tool requirements are:

| Requirement | Local path | Purpose |
| --- | --- | --- |
| `xdelta3.exe` | `tools\bin\xdelta3.exe` | Apply `YGO.Nexus.Revival.0.5.xdelta` and create final XDELTA patches. |
| `DSDecmp.exe` | `tools\bin\DSDecmp.exe` | Decompress/recompress DS compression formats when a file edit needs it. |
| Python virtual environment | `.venv\Scripts\python.exe` | Run repo scripts without needing global Python on PATH. |
| Python packages | `requirements.txt` | Script Nintendo DS ROM/file edits when needed. |

## Local-only files

These are intentionally not committed:

- `.venv`
- `build`
- `tools`
- `YGO2011-Over_The_Nexus_USA_unpatched.nds`
- `.claude`

Do not edit `toDos.txt` or `working_on_instant_win.txt` unless the user explicitly asks for those files.

## Development workflow for builds, releases and validation

Run the full workflow from the repo root by invoking the three scripts in order.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\apply-revival-patch.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\create-xdelta-as-diff.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\validate-xdelta.ps1
```

The scripts apply the Nexus Revival patch, build this repo's Quality ROM, recreate `Quality_Patch.xdelta`, validate the patch output, and print SHA256 hashes for the important files.

## Sources

- xdelta3: https://github.com/jmacd/xdelta-gpl/releases/download/v3.0.11/xdelta3-3.0.11-x86_64.exe.zip
- ndspy: https://pypi.org/project/ndspy/
- DSDecmp source: https://github.com/Barubary/dsdecmp
- DSDecmp binary used locally: https://github.com/johnson-cooper/YGO-NEXUS-REVIVAL/raw/refs/heads/main/boosters/DSDecmp.exe

## SHA256 hashes

Fixed source and tool hashes:

| File | SHA256 |
| --- | --- |
| `YGO2011-Over_The_Nexus_USA_unpatched.nds` | `394A146733D118E0A685D5615213125D5A94FE72F05A3F9F988FA1418EFB5709` |
| `YGO.Nexus.Revival.0.5.xdelta` | `AB86C453B97BED34BFED2377570CEC16B674E63D01B1D67FAF19E6CBE075E182` |
| `tools\bin\xdelta3.exe` | `D81F59B2FE5E8589C0EE9782E231C805084F4D23DFADE413903A4CAD63B4E342` |
| `tools\dist\xdelta3-3.0.11-x86_64.exe.zip` | `ECA90DAAB9CD8388FFA17FB4D6808BB0616CC5D37A7682126485DBA1C79F86BF` |
| `tools\bin\DSDecmp.exe` | `F130DEB521EF18F2BD82DC53AD20A8B491F1E8705DB5F634471EE107174A62E0` |
| `ndspy-4.2.0-py3-none-any.whl` | `D3B03E57EF5BA450E766035E1908293F7A6BA1A738736FAE42B2C66952ABB85B` |

Current generated artifact hashes:

| File | SHA256 |
| --- | --- |
| `build\YGO2011-Nexus-Revival-0.5.nds` | `80BBAB46CADB3194C907BF2290702956DA37936AB6BE5E6A001B35304C066F55` |
| `build\YGO2011-Quality-Nexus.nds` | `0D8A0672B7D2BF2BDF710625C4915D012EC8E057157D00051E578B1E2583F127` |
| `Quality_Patch.xdelta` | `624D8520B04CEE508C4F0C0116581F03D75C5F927E8AB36DEBE37BC91BB9C0DA` |

## Development notes

- Keep generated ROMs under `build`.
- Keep `Quality_Patch.xdelta` in the repo root; it is the distributable patch produced by the build.
- Prefer extending `scripts\apply-quality-patch.py` for ROM changes instead of hand-editing generated ROM output.
- Keep replacements length-safe when editing in-place ROM text.
- Preserve fixed hash checks for base inputs and Revival output.
- If output hashes change because the patcher changed, report the new hash in the final answer and update this file when the hash is meant to be a stable release reference.
