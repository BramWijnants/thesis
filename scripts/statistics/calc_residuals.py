#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 16:10:05 2020

@author: bram
"""
import os
import re
import gdal
import datetime
import numpy as np

def absoluteFilePaths(directory): 
    result = []
    for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f[-3:] == 'tif':
               result.append(os.path.abspath(os.path.join(dirpath, f)))
    return(result)

#input_folder_dwd = '/data/thesis/data_analysis/dwd/6alignIMERG/2015'
input_folder_dwd = '/data/thesis/data_analysis/dwd/7alignOPERA/2015'
#input_folder = '/data/thesis/data_analysis/imerg/4dail/2017/precipitationCal'
input_folder = '/data/thesis/data_analysis/imerg/5aligned_opera/2015/precipitationCal'
#input_folder = '/data/thesis/data_analysis/imerg/5aligned_opera_spline/2017'
#input_folder = '/home/bram/studie/thesis/data_analysis/opera/3tiff_p_d/2015'
output_folder = '/data/thesis/data_analysis/residuals/1res_IMERG_aligned/2015'
#output_folder = '/data/thesis/data_analysis/residuals/1res_IMERG_splined/2017'
#output_folder = '/home/bram/studie/thesis/data_analysis/residuals/1res_OPERA/2015'

# get list of filenames
dwd_filenames = absoluteFilePaths(input_folder_dwd)
opera_filenames = absoluteFilePaths(input_folder)

# create pairs of filenames of the same day list of list?
filenames_paired = []
for i, opera_filename in enumerate(opera_filenames):
    
    date_string_opera = re.search('ERG.20[\d]{6}', opera_filename).group().strip('ERG.')
    date_time = datetime.datetime.strptime(date_string_opera, '%Y%m%d')
    pair_dwd_filename = next(fn for fn in dwd_filenames if date_string_opera in fn)
    filenames_paired.append([date_time, pair_dwd_filename, opera_filename])

# open both files and loop trough them
for date, dwd_filename, opera_filename in filenames_paired:
    dwd_ds = gdal.Open(dwd_filename)
    dwd_array = np.array(dwd_ds.GetRasterBand(1).ReadAsArray())
    
    residuals = np.zeros(dwd_array.shape)
    residuals[residuals == 0] = -9999000
    
    opera_ds = gdal.Open(opera_filename)
    opera_array = np.array(opera_ds.GetRasterBand(1).ReadAsArray())

    for i in range(len(dwd_array)):
        for j in range(len(dwd_array[i])):
            
            dwd_value = dwd_array[i][j]
            opera_value = opera_array[i][j]
            
            if dwd_value != -9999000. and opera_value != -9999000.:
                
                residuals[i][j] = opera_value - dwd_value
    
    output_fn = 'Residuals_IMERG-DWD_'+date.strftime('%Y%m%d')+'.tif'
    full_output_fn = os.path.join(output_folder, output_fn)
    
    #save
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.CreateCopy(full_output_fn, opera_ds)

    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(residuals)
    dst_band.ComputeStatistics(True)
    
    opera_ds.FlushCache()
    dwd_ds.FlushCache()
    dst_ds.FlushCache()
