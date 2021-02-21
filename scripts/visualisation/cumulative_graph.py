#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 12:16:37 2020

@author: bram
"""
import os
import re
import time
import gdal
import numpy as np
import matplotlib.pyplot as plt

def absolute_file_paths(directory_path):
    """
    Parameters
    ----------
    directory_path : string
        String to a directory or folder in which to search for files

    Returns
    -------
    result : list
        List of absolute filenames within the given directory_path that end
        with 'tif'
    """

    result = []
    for dirpath, _, filenames in os.walk(directory_path):
        for filename in filenames:
            if filename.endswith('tif'):
                result.append(os.path.abspath(os.path.join(dirpath, filename)))
    return result

def find_matching_days(path1, path2):
    """
    Parameters
    ----------
    path1 : string
        path to first folder of .tif files with the date in %Y%m%d format
    path2 : string
        path to second folder of .tif files with the date in %Y%m%d format

    Returns
    -------
    result : dictionary
        Dictionary with days as keys and a tuple of filenames with matching date
        for example: filename_dict = {'20151201': (fn_1, fn_2)}
    """

    result = {}
    file_paths1 = absolute_file_paths(path1)
    file_paths2 = absolute_file_paths(path2)

    for filename1 in file_paths1:
        date_string = re.search(r'20[\d]{6}', filename1).group()
        for filename2 in file_paths2:
            if date_string in filename2:
                result[date_string] = (filename1, filename2)
    return result

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
    
    REF_IMERG_PATH = '/home/bram/studie/thesis/data_analysis/dwd/6alignIMERG/2015'
    REF_OPERA_PATH = '/home/bram/studie/thesis/data_analysis/dwd/7alignOPERA/2015'
    IMERG_PATH = '/home/bram/studie/thesis/data_analysis/imerg/4dail/2015/precipitationCal'
    OPERA_PATH = '/home/bram/studie/thesis/data_analysis/opera/3tiff_p_d/2015'
    
    imerg_filenames = find_matching_days(REF_IMERG_PATH, IMERG_PATH)
    opera_filenames = find_matching_days(REF_OPERA_PATH, OPERA_PATH)
    
    days_opera = []
    daily_sum_opera = []
    daily_sum_opera_dwd = []
    
    days_imerg = []
    daily_sum_imerg = []
    daily_sum_imerg_dwd = []
    
    for date, (fn_dwd, fn_opera) in sorted(opera_filenames.items()):

        ds_dwd = gdal.Open(fn_dwd)
        ds_opera = gdal.Open(fn_opera)
        
        band_dwd = ds_dwd.GetRasterBand(1)
        band_opera = ds_opera.GetRasterBand(1)
        
        array_dwd = band_dwd.ReadAsArray()
        array_opera = band_opera.ReadAsArray()
        
        sum_day_dwd = array_dwd[array_dwd != -9999000].sum()
        sum_day_opera = array_opera[array_opera != -9999000].sum()
        
        #date_object = time.strptime(date, '%Y%m%d')
        date_object = date
        days_opera.append(date_object)
        
        if len(daily_sum_opera) == 0:
            daily_sum_opera.append(sum_day_opera)
            daily_sum_opera_dwd.append(sum_day_dwd)
        
        else:
            daily_sum_opera.append(daily_sum_opera[-1] + sum_day_opera)
            daily_sum_opera_dwd.append(daily_sum_opera_dwd[-1] + sum_day_dwd)

    daily_sum_opera_perc = (daily_sum_opera / daily_sum_opera_dwd[-1])*100
    daily_sum_opera_dwd_perc = (daily_sum_opera_dwd / daily_sum_opera_dwd[-1])*100
        
    import pandas as pd
    import plotly.express as px
    import seaborn as sns
    
    opera_df = pd.DataFrame({"Datum": days_opera,
                  "Accumulation opera (%)": daily_sum_opera_perc,
                  "Accumulation dwd (%)": daily_sum_opera_dwd_perc})
    
    opera_df.set_index('Datum').plot(rot=45)
    
    opera_df2 = pd.DataFrame({"Accumulation opera (%)": daily_sum_opera_perc,
                  "Accumulation dwd (%)": daily_sum_opera_dwd_perc})
    opera_df.set_index('Accumulation opera (%)').plot()
    
    for date, (fn_dwd, fn_imerg) in sorted(imerg_filenames.items()):

        ds_dwd = gdal.Open(fn_dwd)
        ds_imerg = gdal.Open(fn_imerg)
        
        band_dwd = ds_dwd.GetRasterBand(1)
        band_imerg = ds_imerg.GetRasterBand(1)
        
        array_dwd = band_dwd.ReadAsArray()
        array_imerg = band_imerg.ReadAsArray()
        
        sum_day_dwd = array_dwd[array_dwd != -9999000].sum()
        sum_day_imerg = array_imerg[array_imerg != -9999000].sum()
        
        #date_object = time.strptime(date, '%Y%m%d')
        date_object = date
        days_imerg.append(date_object)
        
        if len(daily_sum_imerg) == 0:
            daily_sum_imerg.append(sum_day_imerg)
            daily_sum_imerg_dwd.append(sum_day_dwd)
        
        else:
            daily_sum_imerg.append(daily_sum_imerg[-1] + sum_day_imerg)
            daily_sum_imerg_dwd.append(daily_sum_imerg_dwd[-1] + sum_day_dwd)

    daily_sum_imerg_perc = (daily_sum_imerg / daily_sum_imerg_dwd[-1])*100
    daily_sum_imerg_dwd_perc = (daily_sum_imerg_dwd / daily_sum_imerg_dwd[-1])*100
        
    
    imerg_df = pd.DataFrame({"Datum": days_imerg,
                  "Accumulation imerg (%)": daily_sum_imerg_perc,
                  "Accumulation dwd (%)": daily_sum_imerg_dwd_perc})
    
    imerg_df.set_index('Datum').plot(rot=45)
    
    imerg_df2 = pd.DataFrame({"Accumulation imerg (%)": daily_sum_imerg_perc,
                  "Accumulation dwd (%)": daily_sum_imerg_dwd_perc})
    imerg_df.set_index('Accumulation imerg (%)').plot()