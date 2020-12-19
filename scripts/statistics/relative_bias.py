#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 13:22:00 2020

Script to calculate relative bias from OPERA or IMERGresiduals and DWD reference rasters

@author: bram
"""
import os
import re
import numpy as np
import gdal

def relative_bias(filename_dict):
    """
    Parameters
    ----------
    filename_dict : dictionary
        Dictionary with days as keys and a tuple of filenames of
        observations and reference .tif raster files
        for example: filename_dict = {'20151201': (fn_ref, fn_res)}

        residuals are defined as: prediction - reference

    Returns
    -------
    float
        Relative bias of the given rasters by dividing the sum of the
        residuals with the sum of the reference rasters:

        sum(residuals)/sum(reference)
    """

    sum_residual = 0
    sum_reference = 0

    for _, filenames in filename_dict.items():

        fn_ref, fn_res = filenames

        ds_ref = gdal.Open(fn_ref)
        band_ref = ds_ref.GetRasterBand(1)
        array_ref = band_ref.ReadAsArray()

        sum_reference += sum(array_ref[array_ref != -9999000])

        ds_res = gdal.Open(fn_res)
        band_res = ds_res.GetRasterBand(1)
        array_res = band_res.ReadAsArray()

        sum_residual += sum(array_res[array_res != -9999000])

    return sum_residual/sum_reference

def relative_bias_spatial(filename_dict):
    """
    Parameters
    ----------
    filename_dict : dictionary
        Dictionary with days as keys and a tuple of filenames of
        observations and reference .tif raster files
        for example: filename_dict = {'20151201': (fn_ref, fn_res)}

        residuals are defined as: prediction - reference

    Returns
    -------
    float
        Relative bias of the given rasters by dividing the sum of the
        residuals with the sum of the reference rasters:

        sum(residuals)/sum(reference)
    """
    
    first_ds = gdal.Open(list(filename_dict.values())[0][0])
    first_band = first_ds.GetRasterBand(1)
    first_array = first_band.ReadAsArray()
    
    sum_residual = np.zeros(first_array.shape)
    sum_reference = np.zeros(first_array.shape)
    bias = np.zeros(first_array.shape)
    bias[:] = -9999000

    for _, filenames in filename_dict.items():

        fn_ref, fn_res = filenames

        ds_ref = gdal.Open(fn_ref)
        band_ref = ds_ref.GetRasterBand(1)
        array_ref = band_ref.ReadAsArray()

        array_ref[array_ref == -9999000] = 0
        sum_reference += array_ref

        ds_res = gdal.Open(fn_res)
        band_res = ds_res.GetRasterBand(1)
        array_res = band_res.ReadAsArray()

        array_res[array_res == -9999000] = 0
        sum_residual += array_res

    for i, row in enumerate(sum_reference):
        for j, reference_value in enumerate(row):
            
            residual_value = sum_residual[i][j]
            
            if reference_value != 0 and residual_value != 0:
                bias[i][j] = residual_value / reference_value
    
    return bias

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

def FAR(filename_dict, mask=False):
    """
    Parameters
    ----------
    filename_dict : dictionary
        Dictionary with days as keys and a tuple of filenames of
        observations and reference .tif raster files
        for example: filename_dict = {'20151201': (fn_ref, fn_res)}

        residuals are defined as: prediction - reference

    Returns
    -------
    float
        Relative bias of the given rasters by dividing the sum of the
        residuals with the sum of the reference rasters:

        sum(residuals)/sum(reference)
    """

    FP = 0
    total = 0

    if mask:
        ds_mask = gdal.Open(mask)
        array_mask = ds_mask.GetRasterBand(1).ReadAsArray()

    for _, filenames in filename_dict.items():

        fn_ref, fn_obs = filenames

        ds_ref = gdal.Open(fn_ref)
        band_ref = ds_ref.GetRasterBand(1)
        array_ref = band_ref.ReadAsArray()

        ds_obs = gdal.Open(fn_obs)
        band_obs = ds_obs.GetRasterBand(1)
        array_obs = band_obs.ReadAsArray()

        if mask:
    
            for i in range(len(array_ref)):
                for j in range(len(array_ref[i])):
                    
                    value_ref = array_ref[i][j]
                    value_obs = array_obs[i][j]
                    value_mask = array_mask[i][j]
                    
                    if value_mask != 0 and value_ref != -9999000 and value_obs != -9999000:
                        
                        if value_obs > 0 and value_ref == 0:
                            
                            FP += 1
                            total += 1
                            
                        elif value_ref == 0:
                            
                            total += 1
    return FP/total

def RMSE(path_residuals):
    
    residuals = []
    
    filenames_residuals = absolute_file_paths(path_residuals)
    
    for filename in filenames_residuals:
        
        ds = gdal.Open(filename)
        array = ds.GetRasterBand(1).ReadAsArray()
        residuals += array.flatten().tolist()
    
    residuals = [res for res in residuals if res != -9999000]
    standard_deviation = np.std(residuals)
    
    return standard_deviation

def POD(filename_dict, mask=False):
    """
    Parameters
    ----------
    filename_dict : dictionary
        Dictionary with days as keys and a tuple of filenames of
        observations and reference .tif raster files
        for example: filename_dict = {'20151201': (fn_ref, fn_res)}

        residuals are defined as: prediction - reference

    Returns
    -------
    float
        Relative bias of the given rasters by dividing the sum of the
        residuals with the sum of the reference rasters:

        sum(residuals)/sum(reference)
    """

    TP = 0
    total = 0

    if mask:
        ds_mask = gdal.Open(mask)
        array_mask = ds_mask.GetRasterBand(1).ReadAsArray()
        
    for _, filenames in filename_dict.items():

        fn_ref, fn_obs = filenames

        ds_ref = gdal.Open(fn_ref)
        band_ref = ds_ref.GetRasterBand(1)
        array_ref = band_ref.ReadAsArray()

        ds_obs = gdal.Open(fn_obs)
        band_obs = ds_obs.GetRasterBand(1)
        array_obs = band_obs.ReadAsArray()

        if mask:
    
            for i in range(len(array_ref)):
                for j in range(len(array_ref[i])):
                    
                    value_ref = array_ref[i][j]
                    value_obs = array_obs[i][j]
                    value_mask = array_mask[i][j]
                    
                    if value_mask != 0 and value_ref != -9999000 and value_obs != -9999000:
                        
                        if value_obs > 0 and value_ref > 0:
                            
                            TP += 1
                            total += 1
                            
                        elif value_ref > 0:
                            
                            total += 1
    return TP/total

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

    # YEARLY BIAS MAPS IMERG    

    REF_PATH = '/media/bram/Data/thesis/data_analysis/dwd/6alignIMERG/2015'
    RES_PATH = '/media/bram/Data/thesis/data_analysis/residuals/1res_IMERG/2015'
    OPERA_PATH = '/media/bram/Data/thesis/data_analysis/opera/3tiff_p_d/2015'
    MASK = '/home/bram/studie/thesis/data_analysis/mask/test55.tif'
    RES_OPERA_PATH = '/media/bram/Data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'

    fn_dict = find_matching_days(path1=REF_PATH, path2=OPERA_PATH)
    FAR_thingy = FAR(fn_dict, mask=MASK)
    POD_thingy = POD(fn_dict, mask=MASK)
    RMSE_thingy = RMSE(RES_OPERA_PATH)


    fn_dict = find_matching_days(path1=REF_PATH, path2=RES_PATH)
    bias = relative_bias_spatial(fn_dict)
    
    copy_fn = list(fn_dict.values())[0][0]
    output_fn = '/media/bram/Data/thesis/data_analysis/relative_bias/output/relative_bias_IMERG.tif'
    
    write_raster(output_fn, copy_fn, bias)
    
    relative_bias(fn_dict)
    
    # YEARLY BIAS MAPS OPERA

    REF_PATH = '/media/bram/Data/thesis/data_analysis/dwd/7alignOPERA/2015'
    RES_PATH = '/media/bram/Data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'
    
    fn_dict = find_matching_days(path1=REF_PATH, path2=RES_PATH)
    bias = relative_bias_spatial(fn_dict)
    
    copy_fn = list(fn_dict.values())[0][0]
    output_fn = '/media/bram/Data/thesis/data_analysis/relative_bias/output/relative_bias_OPERA_mask.tif'
    
    write_raster(output_fn, copy_fn, bias)


    # MONTHLY BIAS MAPS IMERG
    REF_PATH = '/media/bram/Data/thesis/data_analysis/dwd/6alignIMERG/2015'
    RES_PATH = '/media/bram/Data/thesis/data_analysis/residuals/1res_IMERG/2015'
    
    month_folders = os.listdir(REF_PATH)
    
    for month in month_folders:
        
        month_ref_path = os.path.join(REF_PATH, month)
        fn_dict = find_matching_days(path1=month_ref_path, path2=RES_PATH)
        bias = relative_bias_spatial(fn_dict)
    
        copy_fn = list(fn_dict.values())[0][0]
        output_fn = '/media/bram/Data/thesis/data_analysis/relative_bias/output/IMERG_month/relative_bias_IMERG_{}.tif'.format(month)
    
        write_raster(output_fn, copy_fn, bias)

    # MONTHLY BIAS MAPS OPERA
    
    REF_PATH = '/media/bram/Data/thesis/data_analysis/dwd/7alignOPERA/2015'
    RES_PATH = '/media/bram/Data/thesis/data_analysis/residuals/1res_OPERA/2015'
    
    seasons = {'DJF': ['12', '01', '02'],
               'MAM': ['03', '04', '05'],
               'JJA': ['06', '07', '08'],
               'SON': ['09', '10', '11']}
    
    for season, months in seasons.items():
        
        fn_dict = {}
        for month in months:
            
            month_ref_path = os.path.join(REF_PATH, month)
            fn_dict.update(find_matching_days(path1=month_ref_path, path2=RES_PATH))
        
        bias = relative_bias_spatial(fn_dict)
    
        copy_fn = list(fn_dict.values())[0][0]
        output_fn = '/media/bram/Data/thesis/data_analysis/relative_bias/output/relative_bias_OPERA_{}.tif'.format(season)
    
        write_raster(output_fn, copy_fn, bias)
        
    REF_PATH = '/media/bram/Data/thesis/data_analysis/dwd/6alignIMERG/2015'
    RES_PATH = '/media/bram/Data/thesis/data_analysis/residuals/1res_IMERG/2015'
    
    for season, months in seasons.items():
        
        fn_dict = {}
        for month in months:
            
            month_ref_path = os.path.join(REF_PATH, month)
            fn_dict.update(find_matching_days(path1=month_ref_path, path2=RES_PATH))
        
        bias = relative_bias_spatial(fn_dict)
    
        copy_fn = list(fn_dict.values())[0][0]
        output_fn = '/media/bram/Data/thesis/data_analysis/relative_bias/output/relative_bias_IMERG_{}.tif'.format(season)
    
        write_raster(output_fn, copy_fn, bias)