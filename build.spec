# -*- mode: python ; coding: utf-8 -*-


block_cipher = None
 

a = Analysis(
    ['geotaste/gui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'eventlet.hubs.epolls',
        'eventlet.hubs.kqueue',
        'eventlet.hubs.selects',
        'dns', 
        'dns.dnssec',
        'dns.e164',
        'dns.hash',
        'dns.namedict',
        'dns.tsigkeyring',
        'dns.update',
        'dns.version',
        'dns.asyncquery',
        'dns.asyncresolver',
        'dns.versioned',
        'dns.zone'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

a.datas += Tree('geotaste/assets', 'geotaste/assets')

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Shakespeare_and_Co_Project_Lab_1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='geotaste/assets/SCo_logo_graphic-cropped.ico'
)


app = BUNDLE(
    exe,
    name='Shakespeare_and_Co_Project_Lab_1.app',
    appname='Shakespeare_and_Co_Project_Lab_1',
    icon='geotaste/assets/SCo_logo_graphic-cropped.ico',
    bundle_identifier=None,
)

