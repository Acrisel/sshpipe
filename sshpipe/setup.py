import os
import sys
import re
import codecs

from setuptools import setup
import importlib.util
from distutils.sysconfig import get_python_lib

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
  twine upload -s dist/acrilog-1.0.2.tar.gz

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
metahost = setup_utils.metahost(PACKAGE)
DESCRIPTION = '''sshpipe provide tools to manage ssh channel to remote hosts.'''

AUTHOR = 'Acrisel Team'
AUTHOR_EMAIL = 'support@acrisel.com'
URL = 'https://github.com/Acrisel/sshpipe'

# version_file=os.path.join(PACKAGE, 'VERSION.py')
# with open(version_file, 'r') as vf:
#     vline=vf.read()
#VERSION = vline.strip().partition('=')[2].replace("'", "")
VERSION = setup_utils.read_version(metahost=metahost)

# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent Accord are
# still present in site-packages. See #18115.
overlay_warning = False
if "install" in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))
        
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, PACKAGE))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break
        
scripts=[]
        
# Find all sub packages
packages=list()
for root, dirs, files in os.walk(PACKAGE, topdown=False):
    if os.path.isfile(os.path.join(root,'__init__.py')):
        packages.append(root)

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()
            
META_PATH = os.path.join(PACKAGE, "__init__.py")
META_FILE = read(META_PATH)

def find_meta(meta):
    """
    Extract __*meta*__ from META_FILE.
    """
    meta_match = re.search(
        r"^__{meta}__[ ]*=[ ]*['\"]([^'\"]*)['\"]".format(meta=meta),
        META_FILE, re.M
    )
    if meta_match:
        return meta_match.group(1)
    raise RuntimeError("Unable to find __{meta}__ string.".format(meta=meta))

setup_info={'name': NAME,
 'version': VERSION,
 'url': URL,
 'author': find_meta("author"),
 'author_email': AUTHOR_EMAIL,
 'description': DESCRIPTION,
 'long_description': open("README.rst", "r").read(),
 'license': 'MIT',
 'keywords': 'library logger multiprocessing',
 'packages': packages,
 'scripts' : scripts,
 'install_requires': ['pyyaml>=3.12',
                      'acrilib>=3.0',],
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
