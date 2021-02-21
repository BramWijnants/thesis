#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 12:18:10 2020

@author: bram
"""
import gdal
import os
import numpy as np
import re
import time

def absoluteFilePaths(directory, ext = 'tif'): 
   result = []
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f.endswith(ext):
               result.append(os.path.abspath(os.path.join(dirpath, f)))
   return result

def get_all_values(filePaths):
    
    ds = gdal.Open(filePaths[0])
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray()

    results = [[[] for x in range(len(array[1]))] for y in range(len(array))]

    for filename in filePaths:
        
        ds = gdal.Open(filename)
        band = ds.GetRasterBand(1)
        array = band.ReadAsArray()
        
        for i in range(len(array)):
            for j in range(len(array[i])):
                results[i][j].append(array[i][j])
    
    return results

##############################################################################
##                                M A I N                                   ##
##############################################################################

OPERA_path = '/data/thesis/data_analysis/opera/3tiff_p_d/2015'
DWD_path = '/data/thesis/data_analysis/dwd/7alignOPERA/2015'
#DWD_path = '/data/thesis/data_analysis/dwd/6alignIMERG/2015'
#OPERA_path = '/data/thesis/data_analysis/imerg/4dail/2015/precipitationCal'

filePaths_OPERA = absoluteFilePaths(OPERA_path)
filePaths_DWD = absoluteFilePaths(DWD_path)

shared_DWD = []

for filename in filePaths_OPERA:
    
    date_string = re.search('RATE_[\d]{8}', filename).group()[5:]
    #date_string = re.search('MERG.[\d]{8}', filename).group()[5:]
    date_time = time.strptime(date_string, '%Y%m%d')

    for filename_DWD in filePaths_DWD:
        
        if date_string in filename_DWD:
            
            shared_DWD.append(filename_DWD)

filePaths_OPERA = sorted(filePaths_OPERA)
filePaths_DWD = sorted(shared_DWD)

all_OPERA_values = get_all_values(filePaths_OPERA)
all_DWD_values = get_all_values(filePaths_DWD)

cleaned_pairs = [[[] for x in range(len(all_OPERA_values[1]))] for y in range(len(all_OPERA_values))]

for i in range(len(all_OPERA_values)):
    for j in range(len(all_OPERA_values[i])):
           
        cleaned_list_DWD = []
        cleaned_list_OPERA = []        

        for k in range(len(all_OPERA_values[i][j])):
            
            if all_DWD_values[i][j][k] != -9999000 and all_OPERA_values[i][j][k] != -9999000:    
                cleaned_pairs[i][j].append((all_DWD_values[i][j][k], all_OPERA_values[i][j][k]))

correlations = [[-9999000 for x in range(len(all_OPERA_values[1]))] for y in range(len(all_OPERA_values))]

for i in range(len(correlations)):
    for j in range(len(correlations[i])):
        
        if len(cleaned_pairs[i][j]) >= 10:
            
            DWD_values = [DWD_value for DWD_value, OPERA_value in cleaned_pairs[i][j]] 
            OPERA_values = [OPERA_value for DWD_value, OPERA_value in cleaned_pairs[i][j]] 
            
            correlations[i][j] = np.corrcoef(DWD_values, OPERA_values)[0][1]

ds = gdal.Open(filePaths_DWD[0])
corr_array = np.array(correlations)

#save
output_fn = '/data/thesis/data_analysis/correlation/correlation_OPERA_yearly.tif'
driver = gdal.GetDriverByName('GTiff')
dst_ds = driver.CreateCopy(output_fn, ds)

dst_band = dst_ds.GetRasterBand(1)
dst_band.WriteArray(corr_array) # mx.filled() to prevent weird nodata stuff and smash the mask onto the data
dst_band.ComputeStatistics(True)

ds.FlushCache()
dst_ds.FlushCache()
