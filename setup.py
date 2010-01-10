from distutils.core import setup
from clip2zeus import APP_TITLE, __version__
import sys

extra = dict()

# Make sure we have the appropriate libraries
if sys.platform in ('nt', 'win32'):
    import py2exe
elif sys.platform in ('darwin', ):
    import py2app
    extra = dict(
        app=['clip2zeus/clip2zeus.py'],
    )

excludes = (
    'email.Generator', 'email.Iterators', 'email.Utils',
)

setup(
    name=APP_TITLE,
    version=__version__,
    description='Monitor your clipboard for URLs and automatically shorten them using 2Zeus',
    author='Josh VanderLinden',
    maintainer='Josh VanderLinden',
    license='MIT',
    console=['clip2zeus/clip2zeus.py'],
    scripts=['clip2zeus/clip2zeus'],
    package_dir={'': 'clip2zeus'},
    packages=[''],
    excludes=excludes,
    options={
        'py2exe': dict(
            compressed=1,
            optimize=2,
            bundle_files=1,
            includes = [
                'simplejson',
            ]
        ),
        'py2app': dict(
            iconfile='clip2zeus/res/clip2zeus.icns',
            compressed=1,
            optimize=2,
            plist=dict(
                CFBundleName=APP_TITLE,
                CFBundleShortVersionString=__version__,
                CFBundleGetInfoString='%s %s' % (APP_TITLE, __version__),
                CFBundleExecutable=APP_TITLE,
                CFBundleIdentifier='com.codekoala.%s' % APP_TITLE.lower(),
            )
        ),
    },
    **extra
)

