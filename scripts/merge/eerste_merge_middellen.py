#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 09:35:39 2020

@author: bram
"""
import os
import re
import gdal

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

def calculate_average(filename_imerg, filename_opera, weigth=0.5):
    
    
    
    return 0

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
    
    IMERG_PATH = ''
    OPERA_PATH = ''
    OUTPUT_PATH = ''
    
    matching_pairs = find_matching_days(IMERG_PATH, OPERA_PATH)
    
    copy_ds = gdal.Open(matching_pairs.items()[0][0])
        
    for date, filenames_pair in matching_pairs.items():
        
        filename_imerg, filename_opera = filenames_pair
        average_array = calculate_average(filename_imerg, filename_opera)
        write_raster(average_array, copy_ds)
    
