#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 12:46:38 2020

"""

import os
import numpy as np
import gdal

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

reference_path = '/thesis/data_analysis/opera/3tiff_p_d/2015/RAD_OPERA_RAINFALL_RATE_20150101.tif'
reference_path = '/thesis/data_analysis/opera/3tiff_p_d/2015/RAD_OPERA_RAINFALL_RATE_20150101.tif'

mask_path = '/thesis/map/mask_opera_extended.tif'

ds_mask = gdal.Open(mask_path)
array_mask = ds_mask.GetRasterBand(1).ReadAsArray()

shape_mask = array_mask.shape

new_row = shape_mask[1] * [-9999000]

array_mask = np.vstack([array_mask, new_row])

write_raster('test55.tif', reference_path, array_mask)

