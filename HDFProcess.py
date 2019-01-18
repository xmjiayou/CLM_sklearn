#coding:utf-8
import h5py
import netCDF4
import numpy as np
import os
import sys

def ReadHDF(filename=None, sdsname = None):
    if not os.path.isfile(filename):
        print '%s is not exist, please check this file!!!' %(filename)
        return

    fin = h5py.File(filename, 'r')
    data = fin[sdsname][:]
    fin.close()

    return data

def WriteHDF(filename=None, sdsname=None, data=None, overwrite=1, dictattr=None):
    '''
    mode
            r        Readonly, file must exist
            r+       Read/write, file must exist
            w        Create file, truncate if exists
            w- or x  Create file, fail if exists
            a        Read/write if exists, create otherwise (default)
    :param filename:
    :param sdsname:
    :param data:
    :param overwrite:
    :return:
    '''
    if overwrite == 1:
        fout = h5py.File(filename, 'w')
    else:
        fout = h5py.File(filename, 'r+')

    # fout[sdsname] = data

    # dst = fout.create_dataset(sdsname, data=data, maxshape = (None))
    dst = fout.create_dataset(sdsname, data=data)

    if isinstance(dictattr, dict):
        for key in dictattr:
            dst.attrs[key] = dictattr[key]

    fout.close()

