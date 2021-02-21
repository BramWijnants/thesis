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

def getArray(filename, nodata=False):
    ds = gdal.Open(filename)
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray()
    if nodata:
        masked_array = np.ma.masked_values(array, nodata)
        return masked_array
    else:
        return array

def absoluteFilePaths(directory):
    fns = []
    for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f.endswith('tif'):
               fns.append(os.path.join(dirpath, f))
    return fns

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
    filenames_residuals = absoluteFilePaths(path_residuals)
    
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

def find_matching_days(path1, path2, path3=False):
    result = {}
    file_paths1 = absoluteFilePaths(path1)
    file_paths2 = absoluteFilePaths(path2)
    if path3:
        file_paths3 = absoluteFilePaths(path3)
    for filename1 in file_paths1:
        date_string = re.search(r'20[\d]{6}', filename1).group()
        for filename2 in file_paths2:
            if date_string in filename2:
                if path3:
                    for filename3 in file_paths3:
                        if date_string in filename3:
                            result[date_string] = [filename1, filename2, filename3]
                else:
                    result[date_string] = [filename1, filename2]
    return result

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

def merge_QI(imerg_path, opera_path, opera_qi_path, output_path, threshold):
    
    matching_pairs = find_matching_days(imerg_path, opera_path, opera_qi_path)   
    
    for date, (filename_imerg, filename_opera, filename_qi) in matching_pairs.items():
        
        imerg = getArray(filename_imerg, nodata=-9999000)
        opera = getArray(filename_opera, nodata=-9999000)
        opera_qi = getArray(filename_qi, nodata=-9999000)
        average = np.zeros(opera.shape, dtype=float)
        average[average == 0] = -9999000
        
        for i in range(len(imerg)):
            for j in range(len(imerg[i])):
                
                imerg_value = imerg[i][j]
                opera_value = opera[i][j]
                qi_value = opera_qi[i][j]
                
                if opera_value > threshold and imerg_value != -9999000 and qi_value != -9999000:
                    average[i][j] = (opera_value * qi_value) + (imerg_value * (1 - qi_value))
                elif opera_value >= 0:
                    average[i][j] = opera_value

        output_filename = os.path.join(output_path, 'OPERA_merged_' + date + '.tif')
        write_raster(output_filename, filename_opera, average)

print(time.ctime())




YEAR = '2015'

MASK = '/home/bram/studie/thesis/data_analysis/mask/test55.tif'

IMERG_PATH = os.path.join('/data/thesis/data_analysis/imerg/5aligned_opera', YEAR, 'precipitationCal')
OPERA_PATH = os.path.join('/data/thesis/data_analysis/opera/3tiff_p_d', YEAR)
#REF_PATH = os.path.join('/data/thesis/data_analysis/dwd/7alignOPERA', YEAR)
OPERA_QI_PATH = os.path.join('/data/thesis/data_analysis/opera/3tiff_q_d', YEAR)

OUTPUT_PATH = os.path.join('/data/thesis/data_analysis/merge/QI', YEAR)
#RES_OUTPUT_PATH = os.path.join('/data/thesis/data_analysis/merge/Residuals/QI', YEAR)

#OUTPUT_PATH = OPERA_PATH
#res_path = '/media/bram/Data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'

#OUTPUT_PATH = IMERG_PATH
#RES_OUTPUT_PATH = os.path.join('/media/bram/Data/thesis/data_analysis/merge/Residuals/IMERG', YEAR)
    
threshold = 1

merge_QI(IMERG_PATH, OPERA_PATH, OPERA_QI_PATH, OUTPUT_PATH, threshold)
#calculate_residuals(REF_PATH, OUTPUT_PATH, RES_OUTPUT_PATH, MASK)

#far, pod, rmse, rel_bias, cor = get_summary(REF_PATH, OUTPUT_PATH, RES_OUTPUT_PATH, MASK)

#print('\nSummary for QI-merge with threshold {}:'.format(threshold))
#print('FAR: {}\nPOD: {}\nRMSE: {}\nRelative Bias: {}\nCorrelation: {}'.format(far, pod, rmse, rel_bias, cor))
#print(time.ctime())
    
    

    