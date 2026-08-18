# build.spec
# Build with:  pyinstaller build.spec
#
# Notes on avoiding AV / SmartScreen false positives:
#  - We build --onedir (not --onefile). Onefile exes self-extract to a temp
#    folder at runtime, which is a very common malware packing pattern and
#    gets flagged far more often by heuristic AV engines than a plain
#    folder of files. onedir has none of that extraction behaviour.
#  - version_info is attached so the exe carries real, inspectable
#    metadata (company, product name, version) instead of looking blank.
#  - The exe still needs to be code-signed (see BUILD.md) - packaging
#    choices alone reduce false positives, they don't eliminate SmartScreen
#    "unrecognized publisher" warnings.

block_cipher = None

a = Analysis(
    ['sql_alter_tool/gui.py'],
    pathex=['sql_alter_tool'],
    binaries=[],
    datas=[],
    hiddenimports=['customtkinter'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SQLAlterTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX-packed exes are a well-known AV trigger - keep off
    console=False,       # windowed app, no console flashing behind it
    icon='assets/app_icon.ico',   # optional - remove this line if you don't have one
    version='version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='SQLAlterTool',
)