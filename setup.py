from distutils.command.install import install
from distutils.command.clean import clean
import setuptools
import distutils
import os
import glob
import shutil
import sox_chords

requirements = [
    "pytest",
    "numpy",
    "librosa",
    "matplotlib",
    "requests",
    "pyqtgraph",
    "tqdm",
    "imageio"
]

here = os.path.dirname(__name__)


class CleanCommand(clean):
    """Custom clean command to tidy up the project root."""
    CLEAN_FILES = './build ./dist ./.eggs ./*.pyc ./*.tgz ./*.egg-info'.split(' ')

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        global here

        for path_spec in self.CLEAN_FILES:
            # Make paths absolute and relative to this path
            abs_paths = glob.glob(os.path.normpath(os.path.join(here, path_spec)))
            for path in [str(p) for p in abs_paths]:
                if not path.startswith(here):
                    # Die if path in CLEAN_FILES is absolute + outside this directory
                    raise ValueError("%s is not a path inside %s" % (path, here))
                print('removing %s' % os.path.relpath(path))
                shutil.rmtree(path)


setuptools.setup(
    name='sox_chords',
    version=sox_chords.__version__,
    description='Generating Guitar Chords from Sox',
    url='https://github.com/baudcode/sox-chords',
    author='Malte Koch',
    author_email='malte-koch@gmx.net',
    maintainer='Malte Koch',
    maintainer_email='malte-koch@gmx.net',
    cmdclass={"clean": CleanCommand},
    namespace_packages=['sox_chords'],
    packages=setuptools.find_packages(exclude=['tests', 'tests.*']),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
        ],
    },
    ext_modules=[],
    setup_requires=["matplotlib<3.0"]
)
