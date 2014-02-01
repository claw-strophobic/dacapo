# -*- mode: python -*-
gst_plugin_path = os.environ.get('GST_PLUGIN_PATH')
print gst_plugin_path
# gst_plugin_path = C:\Programme\GStreamer\lib\gstreamer-0.10
gst_path = 'C:\Programme\GStreamer\lib\site-packages\gst-0.10'
HOMEDIR = os.path.expanduser('~')

a = Analysis(['\\temp\\QtFlac2Mp3\\QtFlac2Mp3.py'],
             pathex=['C:\\pyinstaller-2.0'],
             hiddenimports=[],
             hookspath=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=1,
		  name=os.path.join('build\\pyi.win32\\QtFlac2Mp3', 'QtFlac2Mp3.exe'),
          debug=False,
          strip=False,
          upx=False,
          console=False )
coll = COLLECT( exe,
               a.binaries,
               strip=False,
               upx=False,
               name='distQtFlac2Mp3')