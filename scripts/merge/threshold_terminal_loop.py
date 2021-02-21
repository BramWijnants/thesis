#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  9 09:35:39 2020

@author: bram
"""
import os
import re
import numpy as np
import time
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


def relative_bias(ref_path, res_path):
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

    filename_dict = find_matching_days(ref_path, res_path)

    for _, filenames in filename_dict.items():

        fn_ref, fn_res = filenames

        array_ref = getArray(fn_ref)
        array_res = getArray(fn_res)

        sum_reference += sum(array_ref[array_ref != -9999000])
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
    
    first_array = getArray(list(filename_dict.values())[0][0])
    
    sum_residual = np.zeros(first_array.shape)
    sum_reference = np.zeros(first_array.shape)
    bias = np.zeros(first_array.shape)
    bias[:] = -9999000

    for _, filenames in filename_dict.items():

        fn_ref, fn_res = filenames

        array_ref = getArray(fn_ref)
        array_ref[array_ref == -9999000] = 0
        sum_reference += array_ref

        array_res = getArray(fn_res)
        array_res[array_res == -9999000] = 0
        sum_residual += array_res

    for i, row in enumerate(sum_reference):
        for j, reference_value in enumerate(row):
            
            residual_value = sum_residual[i][j]
            
            if reference_value != 0 and residual_value != 0:
                bias[i][j] = residual_value / reference_value
    
    return bias


def FAR(ref_path, opera_path, mask=False):
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
    
    filename_dict = find_matching_days(ref_path, opera_path)

    if mask:
        ds_mask = gdal.Open(mask)
        array_mask = ds_mask.GetRasterBand(1).ReadAsArray()

    for _, filenames in filename_dict.items():
        fn_ref, fn_obs = filenames
        array_ref = getArray(fn_ref)
        array_obs = getArray(fn_obs)

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
        array = getArray(filename)
        residuals += array.flatten().tolist()
    
    residuals = [res for res in residuals if res != -9999000]
    standard_deviation = np.std(residuals)
    
    return standard_deviation


def POD(ref_path, opera_path, mask=False):
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

    filename_dict = find_matching_days(ref_path, opera_path)

    if mask:
        array_mask = getArray(mask)
    
    for _, filenames in filename_dict.items():

        fn_ref, fn_obs = filenames
        array_ref = getArray(fn_ref)
        array_obs = getArray(fn_obs)

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


def calculate_average(imerg_path, opera_path, output_path, thresh):
    
    matching_pairs = find_matching_days(imerg_path, opera_path)   
    
    for date, (filename_imerg, filename_opera) in matching_pairs.items():
        
        imerg = getArray(filename_imerg, nodata=-9999000)
        opera = getArray(filename_opera, nodata=-9999000)
        average = np.zeros(opera.shape, dtype=float)
        average[average == 0] = -9999000
        
        for i in range(len(imerg)):
            for j in range(len(imerg[i])):
                
                imerg_value = imerg[i][j]
                opera_value = opera[i][j]
                
                if opera_value > thresh and imerg_value != -9999000:
                    average[i][j] = (imerg_value * 0.25) + (opera_value * 0.75)
                elif opera_value >= 0:
                    average[i][j] = opera_value

        output_filename = os.path.join(output_path, 'OPERA_merged_' + date + '.tif')
        write_raster(output_filename, filename_opera, average)

def getArray(filename, nodata=False):
    ds = gdal.Open(filename)
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray()
    if nodata:
        masked_array = np.ma.masked_values(array, nodata)
        return masked_array
    else:
        return array


def calculate_residuals(dwd_filenames, opera_filenames, output_folder, mask):
    
    matching_pairs = find_matching_days(dwd_filenames, opera_filenames)
    mask_array = getArray(mask)
    
    # open both files and loop trough them
    for date, filenames in matching_pairs.items():
        
        dwd_filename, opera_filename = filenames
        
        dwd_array = getArray(dwd_filename)
        opera_array = getArray(opera_filename)
        
        residuals = np.zeros(dwd_array.shape)
        residuals[residuals == 0] = -9999000
    
        for i in range(len(dwd_array)):
            for j in range(len(dwd_array[i])):
                
                dwd_value = dwd_array[i][j]
                opera_value = opera_array[i][j]
                
                if dwd_value != -9999000. and opera_value != -9999000. and mask_array[i][j] != 0:
                    
                    residuals[i][j] = opera_value - dwd_value
        
        output_fn = 'Residuals_OPERA-DWD_'+date+'.tif'
        full_output_fn = os.path.join(output_folder, output_fn)
        write_raster(full_output_fn, opera_filename, residuals)
    

def calculate_correlation(ref_path, opera_path, mask):
    
    ref = []
    obs = []
    
    matching_pairs = find_matching_days(ref_path, opera_path)
    
    # open both files and loop trough them
    for _, filenames in matching_pairs.items():
        
        ref_filename, opera_filename = filenames
        
        ref_array = getArray(ref_filename)
        opera_array = getArray(opera_filename)
        mask_array = getArray(mask)
        
        for i in range(len(ref_array)):
            for j in range(len(ref_array[i])):
                
                ref_value = ref_array[i][j]
                opera_value = opera_array[i][j]
                
                if ref_value != -9999000 and opera_value != -9999000 and mask_array[i][j] != 0:

                    ref.append(ref_value)
                    obs.append(opera_value)
    
    return np.corrcoef(ref, obs)[0][1]


def write_raster(output_filename, copy_filename, array):
    
    ds = gdal.Open(copy_filename)
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.CreateCopy(output_filename, ds)
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(array)
    dst_band.ComputeStatistics(True)
    ds.FlushCache()
    dst_ds.FlushCache()


def get_summary(ref_path, merge_path, res_path, mask):
    
    far = FAR(ref_path, merge_path, mask)
    pod = POD(ref_path, merge_path, mask)
    rmse = RMSE(res_path)
    rel_bias = relative_bias(ref_path, res_path)
    cor = calculate_correlation(ref_path, merge_path, mask)
    
    return far, pod, rmse, rel_bias, cor

if __name__ == '__main__':
    
    print(time.ctime())
    
    YEAR = '2015'
    #WEIGTH = list(range(5, 105, 5))
    #WEIGTH = 0.25
    MASK = '/home/bram/studie/thesis/data_analysis/mask/test55.tif'
    threshold = [x/100 for x in range(0, 110, 10)]
        
    IMERG_PATH = os.path.join('/data/thesis/data_analysis/imerg/5aligned_opera', YEAR, 'precipitationCal')
    OPERA_PATH = os.path.join('/data/thesis/data_analysis/opera/3tiff_p_d', YEAR)
    REF_PATH = os.path.join('/data/thesis/data_analysis/dwd/7alignOPERA', YEAR)
    
    OUTPUT_PATH = os.path.join('/data/thesis/data_analysis/merge/Average', YEAR)
    RES_OUTPUT_PATH = os.path.join('/data/thesis/data_analysis/merge/Residuals/Average', YEAR)
    
    #OUTPUT_PATH = OPERA_PATH
    #res_path = '/media/bram/Data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'
    
    #OUTPUT_PATH = IMERG_PATH
    #RES_OUTPUT_PATH = os.path.join('/media/bram/Data/thesis/data_analysis/merge/Residuals/IMERG', YEAR)
    
    results = {}
    
    for thresh in threshold:
        
        calculate_average(IMERG_PATH, OPERA_PATH, OUTPUT_PATH, thresh)
        calculate_residuals(REF_PATH, OUTPUT_PATH, RES_OUTPUT_PATH, MASK)
        
        far, pod, rmse, rel_bias, cor = get_summary(REF_PATH, OUTPUT_PATH, RES_OUTPUT_PATH, MASK)

        results[thresh] = [far, pod, rmse, rel_bias, cor]
        
        print('\nSummary for weigth, '+str(thresh)+':')
        print('FAR: {}\nPOD: {}\nRMSE: {}\nRelative Bias: {}\nCorrelation: {}'.format(far, pod, rmse, rel_bias, cor))
        print(time.ctime())
        
    
    
    