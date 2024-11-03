# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\machine-monitor-api\\systemConfig\\test_sensors.py'],
    pathex=['D:\\machine-monitor-api\\MachineMonitorApi'],
    binaries=[],
    datas=[('D:\\machine-monitor-api\\db.sqlite3', '.')],
    hiddenimports=['MachineMonitorApi.settings',
                    'django',
                    'influxdb',
                    'requests',
                    'rest_framework',
                    'drf_yasg',
                    'systemConfig',
                    'methodConfig',
                    'equipmentStatus',],
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
    a.binaries,
    a.datas,
    [],
    name='test_sensors',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
