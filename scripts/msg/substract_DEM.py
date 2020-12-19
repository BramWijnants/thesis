#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 11:40:09 2020

"""

import os
import gdal
import numpy as np

def getArray(filename, nodata=False):
    ds = gdal.Open(filename)
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray()
    if nodata:
        masked_array = np.ma.masked_values(array, nodata)
        return masked_array
    else:
        return array

def absoluteFilePaths(directory, ext= 'tif'): 
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(ext):
                yield os.path.abspath(os.path.join(dirpath, filename))

def write_raster(output_filename, copy_filename, array):
    ds = gdal.Open(copy_filename)
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.CreateCopy(output_filename, ds)
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(array)
    dst_band.ComputeStatistics(True)
    ds.FlushCache()
    dst_ds.FlushCache()
    return 0

DEM_PATH = '/thesis/data_analysis/dem/srtm_germany_dsm_aligned.tif'
MSG_PATH = '/thesis/data_analysis/MSG/2clip/2015/cth'
OUTPUT_PATH = '/thesis/data_analysis/MSG/4TOV_MV/2015'
TEST_FILE = 'CTOdm20150101000000323SVMSG01MA_cth_warped.tif'

test_path = os.path.join(MSG_PATH, TEST_FILE)
filenames_MSG = absoluteFilePaths(MSG_PATH)

DEM_array = getArray(DEM_PATH)

for MSG_fn in filenames_MSG:
    
    MSG_array = getArray(MSG_fn, -9999000)
    output_array = (MSG_array - DEM_array).filled()
    
    MSG_filename = os.path.split(MSG_fn)[1]
    new_filename = MSG_filename.replace('warped', 'tov_MV')
    new_path = os.path.join(OUTPUT_PATH, new_filename)
    
    write_raster(new_path, MSG_fn, output_array)
    