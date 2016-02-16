# -*- mode: python -*-

block_cipher = None


a = Analysis(['guimain.py'],
             pathex=['C:\\Users\\itaraday\\My Documents\\python\\Report Analyser\\src'],
             binaries=None,
             datas=None,
             hiddenimports=['scipy.special._ufuncs_cxx'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='FunFactFinder',
          debug=False,
          strip=False,
          upx=True,
          console=True )
