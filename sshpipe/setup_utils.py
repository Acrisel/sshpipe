import os
import sys
import re
import codecs
import stat

from distutils.sysconfig import get_python_lib


def read(*parts, encoding="utf8"):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.
    """
    # if not here:
    #     here = os.path.abspath(os.path.dirname(__file__))

    with codecs.open(os.path.join(*parts), "rb", encoding) as f:
        return f.read()


def find_meta(meta, file, error=True):
    """
    Extract __meta__ value from METAFILE.
    file may contain:
        __meta__ = 'value'
        __meta__ = '''value lines '''
    """
    try:
        text = read(file)
    except Exception as err:
        raise RuntimeError("Failed to read file") from err

    tbase = (r"^__{meta}__[ ]*=[ ]*(({sq}(?P<text1>(.*\n*)*?){sq})|"
             "({dq}(?P<text2>(.*\n*)*?){dq}))")

    sbase = (r"^__{meta}__[ ]*=[ ]*(({sq}(?P<text1>([^\n])*?){sq})|"
             "({dq}(?P<text2>([^\n])*?){dq}))")

    triple = tbase.format(meta=meta, sq="'''", dq='"""')
    re_meta_tripple = re.compile(triple, re.M)
    single = sbase.format(meta=meta, sq="'", dq='"')
    re_meta_single = re.compile(single, re.M)
    try:
        meta_match = re_meta_tripple.search(text)
    except Exception:
        meta_match = None

    # This is separated from exception since search may
    # result with None.
    if meta_match is None:
        try:
            meta_match = re_meta_single.search(text)
        except Exception:
            meta_match = None

    if meta_match is not None:
        match1 = meta_match.group('text1')
        match2 = meta_match.group('text2')
        return match1 if match1 is not None else match2

    if error:
        raise RuntimeError("Unable to find __{meta}__ string in {file}."
                           .format(meta=meta, file=file))


def read_meta_or_file(meta, metafile=None, metahost=None, error=True):
    ''' reads meta tag or file for text information.

    if meta exists, return it.  If not, and file exists,
    return its content.

    Args:
        meta: name to look for as in __meta__; e.g.,
            if meta is set to "authors", __authors__ will be  sought.
        metahost: python (.py) file to look for meta definitions.
        metafile: text file to read if meta not found. If none, it will
            look for capital(meta)*

    Returns:
        string of text found.
    '''
    text = None
    if metahost:
        text = find_meta(meta, file=metahost, error=False)
        if text:
            return text

    # if metafile not provided or not found, we need to look for
    # metahost and extract value from __meta__ = 'value'
    # try metafile
    if not metafile:
        folder = os.getcwd()
    elif os.path.isdir(metafile):
        folder = metafile
        metafile = None

    if metafile:
        if not os.path.isfile(metafile):
            raise RuntimeError("Provided metafile not found: {}"
                               .format(metafile))
    else:
        dir_files = os.listdir(folder)
        file_pattern = re.compile(
            r'^({}|{}).*'.format(meta.lower(), meta.upper()))
        options = [file_pattern.match(f) for f in dir_files]
        options = [opt.group(0) for opt in options if opt]
        if len(options) != 1:
            msg = 'Too many options' if len(options) > 1\
                else 'No option'
            raise RuntimeError("{} for metafile '{}'; {}"
                               .format(msg, meta, ', '.join(options)))
        metafile = os.path.join(folder, options[0])

    if metafile:
        if metafile.endswith('.py'):
            text = find_meta(meta, file=metafile, error=False)
        else:
            text = read(metafile)

    if not text and error:
        raise RuntimeError("Provided meta not found or empty: {}"
                           .format(meta))
    return text


def read_authors_(text):
    vlines = [line for line in map(str.strip, text.split('\n')) if line]
    author = ', '.join([line.rpartition(' ')[0] for line in vlines])
    email = ', '.join([line.rpartition(' ')[2] for line in vlines])
    return author, email


def read_authors(tag='authors', metafile=None, metahost=None):
    text = read_meta_or_file(tag, metafile=metafile, metahost=metahost)
    AUTHOR, AUTHOR_EMAIL = read_authors_(text)
    return AUTHOR, AUTHOR_EMAIL


def read_version_(text):
    ''' reads version from  location.

    Args:
        location: PACKAGE path where version.py
    '''
    version = text.strip()  # .partition('=')[2].replace("'", "")
    return version


def read_version(tag='version', metafile=None, metahost=None):
    ''' reads package version from either a metafile (file containing
    the version string. Or from a file that would contain assignment
    to __version__.

    Args:
        tag: the tag that would compose metafile or meta-variable in
            file.
        metafile: a text file that contains version string only.
        file: a file that would contain assignment to meta-var. E.g.,
            __version__ = '1.0.1'

    Returns:
        version string read from metafile or file.
    '''
    text = read_meta_or_file(tag, metafile=metafile, metahost=metahost)
    if text:
        VERSION = read_version_(text)
    else:
        raise RuntimeError("Cannot read {} from metafile: {},"
                           "or metahost: {}".format(tag, metafile,
                                                    metahost))
    return VERSION


def existing_package(package):
    # Warn if we are installing over top of an existing installation. This can
    # cause issues where files that were deleted from a more recent Accord are
    # still present in site-packages. See #18115.
    overlay_warning = False
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local
        # to catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))

    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, package))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after
            # the command is run, so it's more likely to be seen.
            overlay_warning = True
            break
    return existing_path if overlay_warning else None


def find_packages(location):
    # Find all sub packages
    packages = list()
    for root, _, _ in os.walk(location, topdown=False):
        if os.path.isfile(os.path.join(root, '__init__.py')):
            packages.append(root)
    return packages


def metahost(package):
    return os.path.join(package, '__init__.py')


def metafile(package, meta):
    metafile = os.path.join(package, '{}.py'.format(meta.upper()))
    if not os.path.isfile(metafile):
        metafile = os.path.join(package, '{}.py'.format(meta.lower()))
        if not os.path.isfile(metafile):
            metafile = None
    return metafile


def isexe(fpath):
    fstat = os.stat(fpath)
    mode = fstat.st_mode
    x_perm = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    has_x = (mode & x_perm) > 0
    return has_x and os.path.isfile(fpath)


def scripts(package):
    ''' pull all scripts fomr package/bin.This is not limited to
    executables, as some scripts are sources.
    '''
    bindir = os.path.join(package, 'bin')
    scripts = []
    if os.path.isdir(bindir):
        for file in os.listdir(bindir):
            file = os.path.join(bindir, file)
            if os.path.isfile(file) and not file.endswith('__init__.py'):
                scripts += [file]
    return scripts


def packages(package):
    packages_ = []
    for root, _, _ in os.walk(package, topdown=False):
        if os.path.isfile(os.path.join(root, '__init__.py')):
            packages_.append(root)
    return packages_
