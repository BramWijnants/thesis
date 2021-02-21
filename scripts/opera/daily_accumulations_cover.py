#!/usr/bin/env python3
"""
Script to make daily values from the IMERG 30-minute images

It sums the precipitation, converts to mm, and averages the QIND 
The -8888000 (undetect) are set to 0

"""
import os
import gdal

def absoluteFilePaths(directory):
    for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f.endswith('tif'):
               yield os.path.join(dirpath, f)

def write_raster(output_filename, copy_filename, array):
    
    ds = gdal.Open(copy_filename)
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.CreateCopy(output_filename, ds)
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(array)
    dst_band.ComputeStatistics(True)
    ds.FlushCache()
    dst_ds.FlushCache()

input_path = '/home/bram/IMERG_cover/cleaned_1231'
output_path = '/home/bram/github/thesis/cover_data'

filenames = absoluteFilePaths(input_path)

first_fn = next(filenames)
first_file = gdal.Open(first_fn)
first_array = first_file.GetRasterBand(1).ReadAsArray()

#first_array[first_array == -8888000] = 0

for filename in filenames:
            
    file = gdal.Open(filename)
    array = file.GetRasterBand(1).ReadAsArray()

    #array[array == -8888000] = 0
    
    for i in range(len(array)):
        for j in range(len(array[i])):
            if array[i][j] >= 0 and first_array[i][j] >= 0:
                first_array[i][j] += array[i][j]

output_filename = os.path.join(output_path, os.path.split(filename)[1])
write_raster(output_filename, first_fn, first_array)

    