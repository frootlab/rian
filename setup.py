#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

def getfile(filepath = None):
    """Get the content from a file."""

    import codecs
    
    path = getpath(filepath)
    
    with codecs.open(path, encoding = 'utf-8') as file_handler:
        content = file_handler.read()
    
    return content

def getpath(filepath = None):
    """Get absolute filepath from string or iterable."""

    import os

    here = os.path.abspath(os.path.dirname(__file__))

    if not filepath:
        return here
    elif isinstance(filepath, basestring):
        return os.path.join(here, filepath)
    elif isinstance(filepath, (tuple, list)):
        return os.path.join(here, os.path.sep.join(filepath))
    else:
        raise RuntimeError("Invalid filepath given")

def getvars(filepath = None):
    """Get all __VARIABLE__ from given file."""

    import io
    import re

    # get file content
    path = getpath(filepath)
    with io.open(path, encoding = 'utf8') as file_handler:
        content = file_handler.read()

    # parse variables with regular expressions
    key_regex = """__([a-zA-Z][a-zA-Z0-9]*)__"""
    val_regex = """['\"]([^'\"]*)['\"]"""
    regex = r"^[ ]*%s[ ]*=[ ]*%s" % (key_regex, val_regex)
    variables = {}
    for match in re.finditer(regex, content, re.M):
        key = str(match.group(1))
        val = str(match.group(2))
        variables[key] = val
    
    return variables

def setup_libs():

    import setuptools

    pkg = {
        'name': 'nemoa',
        'descfile': 'DESCRIPTION.rst',
        'libdir': 'lib',
        'keywords': 'dataanalysis classification dbn rbm',
        'install_requires': ['numpy', 'networkx', 'matplotlib'],
        'extras_require': {
            'systemsbiology': ['rpy2'],
            'test': ['unittest'] },
        'classifiers': [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering',
            'Operating System :: OS Independent',
            'License :: OSI Approved :: GPLv3',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4' ],
        'entry_points': {
            'console_scripts': ['nemoa = nemoa.scripts.console:main'] }}

    # prepare dynamic package variables
    srcfile = (pkg['libdir'], pkg['name'], '__init__.py')
    for key, val in getvars(srcfile).items(): pkg[key] = val
    pkg['long_description'] = getfile(pkg['descfile'])
    pkg['package_dir'] = { '': pkg['libdir'] }
    pkg['packages'] = setuptools.find_packages(pkg['libdir'])

    # run setup from setuptools
    setuptools.setup(
        name             = pkg['name'],
        version          = pkg['version'],
        description      = pkg['description'],
        url              = pkg['url'],
        author           = pkg['author'],
        author_email     = pkg['email'],
        license          = pkg['license'],
        keywords         = pkg['keywords'],
        package_dir      = pkg['package_dir'],
        packages         = pkg['packages'],
        classifiers      = pkg['classifiers'],
        long_description = pkg['long_description'],
        install_requires = pkg['install_requires'],
        extras_require   = pkg['extras_require'],
        entry_points     = pkg['entry_points'],
        zip_safe         = False )

    return True

def copy_user_data():
    
    import nemoa.common.ospath
    
    src_base = getpath(('data', 'user'))
    tgt_base = nemoa.common.ospath.special('userdata')
    tgt_base = getpath((tgt_base, 'nemoa', 'workspaces'))
    
    nemoa.common.ospath.copytree(src_base, tgt_base)
    
    return True

def copy_shared_data():
    
    import nemoa.common.ospath
    
    src_base = getpath(('data', 'shared'))
    tgt_base = nemoa.common.ospath.special('shareddata')
    tgt_base = getpath((tgt_base, 'nemoa', 'workspaces'))
    
    nemoa.common.ospath.copytree(src_base, tgt_base)
    
    return True

def create_shortcuts():
    
    return True

if __name__ == '__main__':
    setup_libs()
    copy_user_data()
    copy_shared_data()
    create_shortcuts()
