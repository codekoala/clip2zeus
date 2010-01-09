from distutils.core import setup
from clip2zeus import APP_TITLE, __version__
import py2exe
import sys

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
    package_dir={'': 'clip2zeus'},
    packages=[''],
    excludes=excludes,
    options={
        'py2exe': dict(
            compressed=1,
            optimize=0,
            bundle_files=1,
            includes = [
                'simplejson',
            ]
        ),
    }
)

