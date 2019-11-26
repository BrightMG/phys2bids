# -*- coding: utf-8 -*-

import json
import os
import sys

SUPPORTED_FTYPES = ('acq')  # , 'txt', 'mat', ...


def check_input_dir(indir):
    """
    Checks that the given indir doesn't have a trailing '/'
    """
    if indir[-1:] == '/':
        indir = indir[:-1]

    return indir


def check_input_ext(filename, ext):
    """
    Checks that the given file has the given extension
    """
    if filename[-len(ext):] != ext:
        filename = filename + ext

    return filename


def check_input_type(filename, indir):
    """
    Check which supported type is the filename.
    Alternatively, raise an error if file not found or type not supported.
    """
    fftype_found = False
    for ftype in SUPPORTED_FTYPES:
        filename = check_input_ext(filename, ftype)
        if os.path.isfile(os.path.join(indir, filename)):
            fftype_found = True
            break

    if fftype_found:
        print(f'File extension is .{ftype}')
        return filename, ftype
    else:
        raise Exception(f'The file {filename} wasn\'t found in {indir}'
                        f' or {ftype} is not supported yet.\n'
                        f'phys2bids currently supports:'
                        f' {", ".join(SUPPORTED_FTYPES)}')


def path_exists_or_make_it(fldr):
    """
    Check if folder exists, if not make it
    """
    if not os.path.isdir(fldr):
        os.makedirs(fldr)


def check_file_exists(filename):
    """
    Check if file exists.
    """
    if not os.path.isfile(filename) and filename is not None:
        raise FileNotFoundError(f'The file {filename} does not exist!')


def print_info(filename, phys_object):
    """
    Print the info of the input files, using blueprint_input object
    """
    print(f'File {filename} contains:\n')

    for ch in range(2, phys_object.ch_amount):
        print(f'{(ch-2):02d}. {phys_object.ch_name[ch]};'
              f' sampled at {phys_object.freq[ch]} Hz')


def move_file(oldpath, newpath, ext=''):
    """
    Moves file from oldpath to newpath.
    If file already exists, remove it first.
    """
    check_file_exists(oldpath + ext)

    if os.path.isfile(newpath + ext):
        os.remove(newpath + ext)

    os.rename(oldpath + ext, newpath + ext)


def copy_file(oldpath, newpath, ext=''):
    """
    Copy file from oldpath to newpath.
    If file already exists, remove it first.
    """
    from shutil import copy as cp

    check_file_exists(oldpath + ext)

    if os.path.isfile(newpath + ext):
        os.remove(newpath + ext)

    cp(oldpath + ext, newpath + ext)


def writefile(filename, ext, text):
    """
    Produces a textfile of the specified extension `ext`,
    containing the given content `text`
    """
    with open(filename + ext, 'w') as text_file:
        print(text, file=text_file)


def writejson(filename, data, **kwargs):
    """
    Outputs a json file with the given data inside.
    """
    if not filename.endswith('.json'):
        filename += '.json'
    with open(filename, 'w') as out:
        json.dump(data, out, **kwargs)


def load_heuristic(heuristic):
    """ Loads `heuristic`, returning a callable Python module

    References
    ----------
    Copied from [nipy/heudiconv](https://github.com/nipy/heudiconv)
    Copyright [2014-2019] [Heudiconv developers], Apache 2 license.
    """
    if os.path.sep in heuristic or os.path.lexists(heuristic):
        heuristic_file = os.path.realpath(heuristic)
        path, fname = os.path.split(heuristic_file)
        try:
            old_syspath = sys.path[:]
            sys.path.append(path)
            mod = __import__(fname.split('.')[0])
            mod.filename = heuristic_file
        finally:
            sys.path = old_syspath
    else:
        from importlib import import_module
        try:
            mod = import_module(f'phys2bids.heuristics.{heuristic}')
            # remove c or o from pyc/pyo
            mod.filename = mod.__file__.rstrip('co')
        except Exception as exc:
            raise ImportError(f'Failed to import heuristic {heuristic}: {exc}')
    return mod
