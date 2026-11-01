# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

llama_datas, llama_binaries, llama_hidden = collect_all('llama_cpp')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=llama_binaries,
    datas=llama_datas + [('prompts', 'prompts')],
    hiddenimports=llama_hidden + ['customtkinter', 'PIL', 'llama_cpp'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Onedir instead of onefile — avoids extraction path bugs
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Astra-Codex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Astra-Codex',
)
