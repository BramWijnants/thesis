#!/usr/bin/env python3
"""
Script to convert the 5-minute .asc files (created by dwd_import.py) to daily
accumulations


"""
import os
import gdal
import numpy as np
import time

start_time = time.time() # starttime to print total runtime in the end

# function to create a list of absolute filenames ending with 'asc'
def absoluteFilePaths(directory):  
   result = []
   for dirpath,_,fns in os.walk(directory):
       for f in fns:
           if f[-3:] == 'asc':
               result.append(os.path.abspath(os.path.join(dirpath, f)))   
   return(result)

#input folder (monthly) and output folder
input_folder = '/thesis/data_analysis/dwd/3aai/2017/12'
output_folder = '/thesis/data_analysis/dwd/4aai/2017/12'

# get all directory names (one for every day) in the month folder
day_directories = os.listdir(input_folder)

#loop trough the daily directories
for day_directory in day_directories:
    
    #create filennames of all files ending with asc in the day folder
    filenames = absoluteFilePaths(os.path.join(input_folder, day_directory))
    
    #open first file and get the data as a masked numpy array
    ds = gdal.Open(filenames[0])
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray()
    mx = np.ma.masked_values(array, -9999)
    
    #loop trough the other filenames and add the values
    for filename in filenames[1:]:
        ds2 = gdal.Open(filename)
        band2 = ds2.GetRasterBand(1)
        array2 = band2.ReadAsArray()
        mx2 = np.ma.masked_values(array2, -9999)
        mx += mx2
    
    #check for too high or too low values
    if mx.data.max() > 100 or mx.data.min() != -9999:
        print(day_directory, mx.data.max(), mx.data.min())
    
    #save
    output_fn = os.path.join(output_folder, day_directory)+'.tif'
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.CreateCopy(output_fn, ds)

    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(mx.filled()) # mx.filled() to prevent weird nodata stuff and smash the mask onto the data
    dst_band.ComputeStatistics(True)
    
    ds.FlushCache()
    ds2.FlushCache()
    dst_ds.FlushCache()
    
print("--- %s seconds ---" % (time.time() - start_time))