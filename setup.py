from distutils.core import setup
from clip2zeus import APP_TITLE, __version__, __author__
import sys

extra = dict()
excludes = []

# Make sure we have the appropriate libraries
if sys.platform in ('nt', 'win32'):
    import py2exe
    excludes = [
        'email.Generator', 'email.Iterators', 'email.Utils',
    ]

    class Target(object):
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.version = __version__
            self.company_name = __author__
            self.copyright = 'Copyright 2010 Josh VanderLinden'
            self.name = APP_TITLE

    service = Target(
        description="Clip2Zeus URL Shortening Service",
        modules=['clip2zeus.clip2zeus_service'],
        cmdline_style='pywin32',
    )

    gui = Target(
        description="Clip2Zeus GUI",
        script='clip2zeus/gui.py',
        dest_base='tkclip2zeus',
    )

    extra = dict(
        console=[
            'clip2zeus/clip2zeus_ctl.py',
            'clip2zeus/main.py',
        ],
        service=[service],
        windows=[gui],
    )
elif sys.platform in ('darwin', ):
    import py2app
    extra = dict(
        app=['clip2zeus/main.py'],
    )

setup(
    name=APP_TITLE,
    version=__version__,
    description='Monitor your clipboard for URLs and automatically shorten them using 2Zeus',
    long_description="""This application runs in the background on your Windows, OSX, or Linux machine and
        periodically polls your system clipboard.  If a URL is found somewhere in your
        clipboard, the application will attempt to shorten the URL using http://2ze.us/""",
    keywords='url-shortening, utilities',
    author=__author__,
    author_email='codekoala at gmail com',
    maintainer=__author__,
    maintainer_email='codekoala at gmail com',
    url='http://www.codekoala.com/',
    license='MIT',
    scripts=[
        'clip2zeus/scripts/clip2zeus',
        'clip2zeus/scripts/clip2zeusctl',
        'clip2zeus/scripts/tkclip2zeus',
    ],
    package_dir={'clip2zeus': 'clip2zeus'},
    packages=['clip2zeus'],
    py_modules=[
        'clip2zeus.common',
        'clip2zeus.config',
        'clip2zeus.globals',
        'clip2zeus.main',
    ],
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
                'win32serviceutil',
                'win32service',
                'win32clipboard',
                'clip2zeus.common',
                'Tkinter',
            ],
            excludes=excludes,
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

