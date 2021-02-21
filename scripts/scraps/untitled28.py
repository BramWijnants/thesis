#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  4 11:18:47 2021

Script to calculate the average yearly quality index

@author: bram
"""
import os
import numpy as np
import gdal

def absoluteFilePaths(directory): 
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f[-3:] == 'tif':
               yield os.path.abspath(os.path.join(dirpath, f))

def getArray(filename):
    ds = gdal.Open(filename)
    array = ds.GetRasterBand(1).ReadAsArray()
    #masked_array = np.ma(func, iter1)ds.GetRasterBand(1).ReadAsArray()
    return array

def write_raster(output_filename, copy_filename, array):
    
    ds = gdal.Open(copy_filename)
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.CreateCopy(output_filename, ds)
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(array)
    dst_band.ComputeStatistics(True)
    ds.FlushCache()
    dst_ds.FlushCache()

if __name__ == '__main__':
    
    opera_qind_path = '/data/thesis/data_analysis/opera/3tiff_q_d/2015'
    output_name = '/data/thesis/data_analysis/qind/yearly_average_qind.tif'
    
    
    qind_fns = absoluteFilePaths(opera_qind_path)
    
    base_array = getArray(next(qind_fns))
    count = np.zeros(base_array.shape)
    count[base_array != -9999000] += 1
    base_array[base_array == -9999000] = 0
    
    for filename in qind_fns:
        
        array = getArray(filename)
        count[array != -9999000] += 1
        array[array == -9999000] = 0
        base_array += array
        
    base_array[count != 0] /= count[count != 0]
    base_array[base_array == 0] = -9999000
    
    write_raster(output_name, filename, base_array)
    
