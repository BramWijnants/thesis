#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 13:00:29 2020

@author: bram
"""
import os
import gdal
import numpy as np
import re
import time

def absoluteFilePaths(directory): 
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f[-3:] == 'tif':
               yield os.path.abspath(os.path.join(dirpath, f))

def getValues(filename):
    ds = gdal.Open(filename)
    array = ds.GetRasterBand(1).ReadAsArray()
    value_list = array.tolist()
    return value_list
    

#input_folder_dwd = '/data/thesis/data_analysis/dwd/6alignIMERG/2015/'
input_folder_dwd = '/data/thesis/data_analysis/dwd/7alignOPERA/2015'
#input_folder = '/data/thesis/data_analysis/imerg/4dail/2015/precipitationCal'
input_folder = '/data/thesis/data_analysis/imerg/5aligned_opera/2015/precipitationCal'
#input_folder = '/data/thesis/data_analysis/imerg/5aligned_opera_spline/2015/precipitationCal'
#input_folder = '/home/bram/studie/thesis/data_analysis/opera/3tiff_p_d/2015'
#output_folder = '/home/bram/studie/thesis/data_analysis/residuals/1res_IMERG/2015'

results = {}

filename_generator_IMERG = absoluteFilePaths(input_folder)
filename_generator_DWD = absoluteFilePaths(input_folder_dwd)

for filename_IMERG in filename_generator_IMERG:
    
    #date_string_IMERG = re.search('_RATE_20\d{6}', filename_IMERG).group()[6:]
    date_string_IMERG = re.search('IMERG.20\d{6}', filename_IMERG).group()[6:]
    date_IMERG = time.strptime(date_string_IMERG, '%Y%m%d')
    month = date_IMERG.tm_mon
    values_IMERG = getValues(filename_IMERG)
    
    filename_generator_DWD = absoluteFilePaths(input_folder_dwd)
    
    for filename_DWD in filename_generator_DWD:
    
        date_string_DWD = re.search('_20\d{6}_', filename_DWD).group().strip('_')
        date_DWD = time.strptime(date_string_DWD, '%Y%m%d')
        
        if date_IMERG == date_DWD:
            
            values_DWD = getValues(filename_DWD)
            
            for i in range(len(values_IMERG)):
                for j in range(len(values_IMERG[i])):
                    
                    value_DWD = values_DWD[i][j]
                    value_IMERG = values_IMERG[i][j]
                    
                    if value_IMERG != -9999000 and value_DWD != -9999000:
                        
                        if month not in results.keys():
                            results[month] = [(value_DWD, value_IMERG)]
                            
                        else:
                            results[month].append((value_DWD, value_IMERG))

yearly_dwd_list = []
yearly_imerg_list = []

for month in results:
    
    DWD_list = []
    IMERG_list = []

    
    for value_DWD, value_IMERG in results[month]:
        
        DWD_list.append(value_DWD)
        IMERG_list.append(value_IMERG)
        yearly_imerg_list.append(value_IMERG)
        yearly_dwd_list.append(value_DWD)
        
    DWD_array = np.array(DWD_list)
    IMERG_array = np.array(IMERG_list)    

    r = np.corrcoef(DWD_array, IMERG_array)    
    
    print('Correlation between daily IMERG and DWD estimates for month #'+str(month),'is', r[0][1])

DWD_array = np.array(yearly_dwd_list)
IMERG_array = np.array(yearly_imerg_list)    

r = np.corrcoef(DWD_array, IMERG_array)    

print('Correlation between daily IMERG and DWD estimates for the year 2015 is ', r[0][1])
