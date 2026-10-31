# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all
import os
import llama_cpp

llama_datas, llama_binaries, llama_hidden = collect_all('llama_cpp')

# Extra explicit collection of the lib folder
llama_lib_dir = os.path.join(os.path.dirname(llama_cpp.__file__), 'lib')
extra_binaries = []
if os.path.isdir(llama_lib_dir):
    for root, dirs, files in os.walk(llama_lib_dir):
        for f in files:
            if f.endswith(('.dll', '.so', '.dylib')):
                src = os.path.join(root, f)
                dest = os.path.join('llama_cpp', 'lib', os.path.relpath(src, llama_lib_dir))
                extra_binaries.append((src, dest))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=llama_binaries + extra_binaries,
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Astra-Codex',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir='.',   # extract temp right next to the EXE
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
