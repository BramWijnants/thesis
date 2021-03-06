#!/usr/bin/env python3
"""
Script to make daily values from the IMERG 30-minute images

It sums the precipitation, converts to mm, and averages the QIND 
The -8888000 (undetect) are set to 0

            !!!!!!!!!!!!!!!  D O   N O T    U S E  !!!!!!!!!!!!
            !!!!!!!!!!!!!!!  D O   N O T    U S E  !!!!!!!!!!!!

"""
import os
import gdal

def absoluteFilePaths(directory):
    result = []
    for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f[-3:]=='tif':
               result.append(os.path.join(dirpath, f))
    return result

input_path = '/home/bram/studie/thesis/data_analysis/opera/2tiff_p/2015'
output_path = '/home/bram/studie/thesis/data_analysis/opera/3tiff_p_d/2015'

months = os.listdir(input_path)

for month_dir in months:
    
    month_path = os.path.join(input_path, month_dir)
    days = os.listdir(month_path)
    
    for day in days:
        
        days_path = os.path.join(month_path, day)
        filenames = absoluteFilePaths(days_path)
            
        first_file = gdal.Open(filenames[0])
        first_array = first_file.GetRasterBand(1).ReadAsArray()
        first_array[first_array == -8888000] = 0
        
        for filename in filenames[1:]:
                    
            file = gdal.Open(filename)
            array = file.GetRasterBand(1).ReadAsArray()
            array[array == -8888000] = 0
            
            for i in range(len(array)):
                for j in range(len(array[i])):
                    if array[i][j] != -9999000 and first_array[i][j] != -9999000:
                        first_array[i][j] += array[i][j]
                    else:
                        first_array[i][j] = -9999000

        output_filename = os.path.join(output_path, os.path.split(filename)[1])        

        driver = gdal.GetDriverByName('GTiff')
        dst_ds = driver.CreateCopy(output_filename, first_file)
        dst_band = dst_ds.GetRasterBand(1)
        dst_band.WriteArray(first_array)
        dst_band.FlushCache()
        dst_band.ComputeStatistics(False)
    
    print('month done')
        