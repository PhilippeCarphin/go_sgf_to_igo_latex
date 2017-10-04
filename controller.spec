# -*- mode: python -*-

block_cipher = None


a = Analysis(['controller.py'],
             pathex=['C:\\Users\\phil1\\Documents\\GitHub\\go_sgf_to_igo_latex'],
             binaries=[],
             datas=[('nassima_phil.sgf', '.')],
             hiddenimports=[ ],
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
          exclude_binaries=True,
          name='controller',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='controller')
