# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/chris/PycharmProjects/DxPyGuide/DxPyGuide.py'],
    pathex=[],
    binaries=[],
    datas=[('C:/Users/chris/PycharmProjects/DxPyGuide/icon.ico', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/assert_verdoppeln_grafik.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_age.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_append.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_comprehension.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_dict.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_exceptions.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_file_encryption.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_files.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_functions.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_hello.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_list-input.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_list-validation.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_lists.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_login.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_loops.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_modules.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_oop.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_operators.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_person.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_python-basics.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_testing.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_tuples.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_types.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_ui.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/guide_while.png', '.'), ('C:/Users/chris/PycharmProjects/DxPyGuide/Logo.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DxPyGuide',
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
    icon=['C:/Users/chris/PycharmProjects/DxPyGuide/icon.ico'],
    contents_directory='.',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DxPyGuide',
)
