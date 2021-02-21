#!/usr/bin/env python3
"""
Script to make daily values from the IMERG 30-minute images
I made the map structure with sort_IMERG.py

It sums the precipitationCal and Uncal which are already transformed to mm 
in the IMERG.py step. The QualityIndex and randomError are averaged.
"""
import os
import gdal
import numpy as np

def absoluteFilePaths(directory):
    result = []
    for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f.endswith('tif'):
               result.append(os.path.join(dirpath, f))
    return result

input_folder = '/data/thesis/data_analysis/imerg/3clip/2017'
output_folder = '/data/thesis/data_analysis/imerg/4dail/2017'

datasets = ['precipitationCal', 'precipitationUncal', 'precipitationQualityIndex', 'randomError']

months = os.listdir(input_folder)

for month_dir in months:
    
    month_path = os.path.join(input_folder, month_dir)
    days = os.listdir(month_path)
    
    for day in days:
        
        days_path = os.path.join(month_path, day)
        filenames = absoluteFilePaths(days_path)
        
        for dataset in datasets:
            
            filenames_dataset = [fn for fn in filenames if dataset in fn]
            
            first_file = gdal.Open(filenames_dataset[0])
            first_array = np.array(first_file.GetRasterBand(1).ReadAsArray())
            first_masked_data = np.ma.masked_values(first_array, -9999000.)
            
            for filename in filenames_dataset[1:]:
                
                file = gdal.Open(filename)
                array = np.array(file.GetRasterBand(1).ReadAsArray())
                masked_data = np.ma.masked_values(array, -9999000.)
                
                first_masked_data += masked_data
                
            if dataset == 'precipitationQualityIndex': 
                first_masked_data /= 48
                
            
            output_path = os.path.join(output_folder, dataset)
            
            if not os.path.exists(output_path):
                os.system('mkdir {}'.format(output_path))
            
            name = os.path.split(filename)[1]
            driver = gdal.GetDriverByName('GTiff')
            dst_ds = driver.CreateCopy(os.path.join(output_path, name), first_file)
        
            dst_band = dst_ds.GetRasterBand(1)
            dst_band.WriteArray(first_masked_data.filled())
            dst_band.FlushCache()
            dst_band.ComputeStatistics(False)
