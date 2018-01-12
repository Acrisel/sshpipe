import sys

from setuptools import setup
import importlib.util

''' 
is the Python package in your project. It's the top-level folder containing the 
__init__.py module that should be in the same directory as your setup.py file
/-
  |- README.rst
  |- CHANGES.txt
  |- setup.py
  |- dogs 
     |- __init__.py
     |- catcher.py

To create package and upload:

  python setup.py register
  python setup.py sdist
  twine upload -s dist/package.tar.gz

'''


def import_setup_utils():
    # load setup utils
    try:
        setup_utils_spec = \
            importlib.util.spec_from_file_location("setup.utils",
                                                   "setup_utils.py")
        setup_utils = importlib.util.module_from_spec(setup_utils_spec)
        setup_utils_spec.loader.exec_module(setup_utils)
    except Exception as err:
        raise RuntimeError("Failed to find setup_utils.py."
                           " Please copy or link.") from err
    return setup_utils


setup_utils = import_setup_utils()
PACKAGE = "sshpipe"
NAME = PACKAGE
DESCRIPTION = ('sshpipe provide tools to manage ssh channel to remote hosts.')

metahost = setup_utils.metahost(PACKAGE)
AUTHORS, AUTHOR_EMAILS = setup_utils.read_authors(metahost=metahost)
URL = 'https://github.com/Acrisel/sshpipe'
VERSION = setup_utils.read_version(metahost=metahost)

# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent Accord are
# still present in site-packages. See #18115.
overlay_warning = False
if "install" in sys.argv:
    existing_path = setup_utils.existing_package(PACKAGE)

scripts = setup_utils.scripts(PACKAGE)

# Find all sub packages
packages = setup_utils.packages(PACKAGE)
required = setup_utils.read_required(metahost=metahost)

setup_info={
    'name': NAME,
    'version': VERSION,
    'url': URL,
    'author': AUTHORS,
    'author_email': AUTHOR_EMAILS,
    'description': DESCRIPTION,
    'long_description': open("README.rst", "r").read(),
    'license': 'MIT',
    'keywords': 'library logger multiprocessing',
    'packages': packages,
    'scripts': scripts,
    'install_requires': required,
    'extras_require': {'dev': [], 'test': []},
    'classifiers': ['Development Status :: 4 - Beta',
                    'Environment :: Other Environment',
                    #'Framework :: Project Settings and Operation',
                    'Intended Audience :: Developers',
                    'License :: OSI Approved :: MIT License',
                    'Operating System :: OS Independent',
                    'Programming Language :: Python',
                    'Programming Language :: Python :: 3',
                    'Topic :: System :: Distributed Computing',
                    'Topic :: Software Development :: Libraries :: Python '
                    'Modules']}
setup(**setup_info)


if overlay_warning:
    sys.stderr.write("""

========
WARNING!
========

You have just installed %(name)s over top of an existing
installation, without removing it first. Because of this,
your install may now include extraneous files from a
previous version that have since been removed from
Accord. This is known to cause a variety of problems. You
should manually remove the

%(existing_path)s

directory and re-install %(name)s.

""" % {"existing_path": existing_path, 'name': NAME})
