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


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='sox_chords',
    version=sox_chords.__version__,
    description='Generating Guitar Chords using sox',
    url='https://github.com/baudcode/sox-chords',
    author='Malte Koch',
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url='https://github.com/baudcode/sox-chords/archive/v%s.tar.gz' % (sox_chords.__version__),
    keywods=["chords", "scales", "notes", "guitar", "sox"],
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
    setup_requires=["matplotlib<3.0"],
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
