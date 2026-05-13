## Requirements

`requirements.txt` only lists Python packages. The full local tool requirements are:

| Requirement | Local path | Purpose |
| --- | --- | --- |
| `xdelta3.exe` | `tools\bin\xdelta3.exe` | Apply `YGO.Nexus.Revival.0.5.xdelta` and create final XDELTA patches. |
| `DSDecmp.exe` | `tools\bin\DSDecmp.exe` | Decompress/recompress DS compression formats when a file edit needs it. |
| Python virtual environment | `.venv\Scripts\python.exe` | Run repo scripts without needing global Python on PATH. |
| Python packages | `requirements.txt` | Script Nintendo DS ROM/file edits when needed. |

The `tools\bin` binaries and `.venv` are ignored by git. Keep them installed locally, but do not commit them unless we decide to vendor tools later. Check `requirements.txt` for the exact Python packages to install when Python scripting is needed.

## Patch workflow

Apply the Nexus Revival starting patch without a GUI:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\apply-revival-patch.ps1
```

The script writes `build\YGO2011-Nexus-Revival-0.5.nds`.

Build this repo's Quality patch without a GUI:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\create-xdelta-as-diff.ps1
```

The script writes `build\YGO2011-Quality-Nexus.nds`, creates `Quality_Patch.xdelta`, and verifies that the patch recreates the same ROM.

Validate this repo's Quality patch without keeping a second ROM:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\validate-xdelta.ps1
```

## Sources

- xdelta3: https://github.com/jmacd/xdelta-gpl/releases/download/v3.0.11/xdelta3-3.0.11-x86_64.exe.zip
- ndspy: https://pypi.org/project/ndspy/
- DSDecmp source: https://github.com/Barubary/dsdecmp
- DSDecmp binary used locally: https://github.com/johnson-cooper/YGO-NEXUS-REVIVAL/raw/refs/heads/main/boosters/DSDecmp.exe

## SHA256 hashes

| File | SHA256 |
| --- | --- |
| `YGO2011-Over_The_Nexus_USA_unpatched.nds` | `394A146733D118E0A685D5615213125D5A94FE72F05A3F9F988FA1418EFB5709` |
| `YGO.Nexus.Revival.0.5.xdelta` | `AB86C453B97BED34BFED2377570CEC16B674E63D01B1D67FAF19E6CBE075E182` |
| `build\YGO2011-Nexus-Revival-0.5.nds` | `80BBAB46CADB3194C907BF2290702956DA37936AB6BE5E6A001B35304C066F55` |
| `Quality_Patch.xdelta` | `B35A99612F15F2B7DAB9386DF6FA6854A40B14468F5D35DDDD73915210ADE359` |
| `build\YGO2011-Quality-Nexus.nds` | `D8EC9A83E85A0B8F54B96F0AB401034D65839DB455FCFF6695EE7C875FDDA963` |
| `tools\bin\xdelta3.exe` | `D81F59B2FE5E8589C0EE9782E231C805084F4D23DFADE413903A4CAD63B4E342` |
| `tools\dist\xdelta3-3.0.11-x86_64.exe.zip` | `ECA90DAAB9CD8388FFA17FB4D6808BB0616CC5D37A7682126485DBA1C79F86BF` |
| `tools\bin\DSDecmp.exe` | `F130DEB521EF18F2BD82DC53AD20A8B491F1E8705DB5F634471EE107174A62E0` |
| `ndspy-4.2.0-py3-none-any.whl` | `D3B03E57EF5BA450E766035E1908293F7A6BA1A738736FAE42B2C66952ABB85B` |
