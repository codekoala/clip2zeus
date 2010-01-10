from distutils.core import setup
from clip2zeus import APP_TITLE, __version__
import sys

extra = dict()

# Make sure we have the appropriate libraries
if sys.platform in ('nt', 'win32'):
    import py2exe
    excludes = (
        'email.Generator', 'email.Iterators', 'email.Utils',
    )

    extra = dict(
        console=['clip2zeus/clip2zeus.py'],
        excludes=excludes,
    )
elif sys.platform in ('darwin', ):
    import py2app
    extra = dict(
        app=['clip2zeus/clip2zeus.py'],
    )

setup(
    name=APP_TITLE,
    version=__version__,
    description='Monitor your clipboard for URLs and automatically shorten them using 2Zeus',
    long_description="""This application runs in the background on your Windows, OSX, or Linux machine and
        periodically polls your system clipboard.  If a URL is found somewhere in your
        clipboard, the application will attempt to shorten the URL using http://2ze.us/""",
    keywords='url-shortening, utilities',
    author='Josh VanderLinden',
    author_email='codekoala at gmail com',
    maintainer='Josh VanderLinden',
    maintainer_email='codekoala at gmail com',
    url='http://www.codekoala.com/',
    license='MIT',
    scripts=['clip2zeus/clip2zeus'],
    package_dir={'': 'clip2zeus'},
    packages=[''],
    platforms=[
        'Windows',
        'OSX',
        'Linux',
    ],
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
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Topic :: Utilities',
    ],
    **extra
)

