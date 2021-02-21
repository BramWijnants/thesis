#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 15:13:58 2021

@author: bram
"""
import os
import re
import gdal

def absoluteFilePaths(directory_path):
    result = []
    for dirpath, _, filenames in os.walk(directory_path):
        for filename in filenames:
            if filename.endswith('tif'):
                result.append(os.path.abspath(os.path.join(dirpath, filename)))
    return result

def find_matching_days(path1, path2, path3):
    result = {}
    
    file_paths1 = absoluteFilePaths(path1)
    file_paths2 = absoluteFilePaths(path2)
    file_paths3 = absoluteFilePaths(path3)
    
    for filename1 in file_paths1:
        date_string = re.search(r'20[\d]{6}', filename1).group()
        for filename2 in file_paths2:
            if date_string in filename2:
                for filename3 in file_paths3:
                    if date_string in filename3:
                        result[date_string] = [filename1, filename2, filename3]
    return result

def getArray(filename):
    ds = gdal.Open(filename)
    array = ds.GetRasterBand(1).ReadAsArray()
    return array


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

    REF_PATH = '/home/bram/Data/thesis/data_analysis/dwd/7alignOPERA/2015'
    QIND_PATH = '/home/bram/Data/thesis/data_analysis/opera/3tiff_q_d/2015'
    RES_PATH = '/home/bram/Data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'

    fn_dict = find_matching_days(path1=RES_PATH, path2=QIND_PATH, path3=REF_PATH)

    cum_ress = [0,0,0,0,0]
    cum_ref = [0,0,0,0,0]

    for _,fns in fn_dict.items():
        
        res_fn, qind_fn, ref_fn = fns
        
        res_array = getArray(res_fn)
        qind_array = getArray(qind_fn)
        ref_array = getArray(ref_fn)
        
        for i in range(len(res_array)):
            for j in range(len(res_array[i])):
                
                qind = qind_array[i][j]
                res = res_array[i][j]
                ref = ref_array[i][j]
                
                if qind != -9999000 and res != -9999000 and ref != -9999000:
                
                    if qind <= 0.2:
                        
                        cum_ress[0] += res
                        cum_ref[0] += ref
                    
                    elif qind <= 0.4:
                        
                        cum_ress[1] += res
                        cum_ref[1] += ref
                        
                    elif qind <= 0.6:
                        
                        cum_ress[2] += res
                        cum_ref[2] += ref
                        
                    elif qind <= 0.8:
                        
                        cum_ress[3] += res
                        cum_ref[3] += ref
                        
                    elif qind <= 1:
                        
                        cum_ress[4] += res
                        cum_ref[4] += ref    
                
    
    qinds = [0,0.2,0.4,0.6,0.8,1,1]
    
    for i, residual in enumerate(cum_ress):
        
        ref = cum_ref[i]
        bias = residual / ref
        
        print("OPERA's Relative bias for Qind between {} and {} is: {}".format(qinds[i],qinds[i+1],bias))
        
        
        
        
        

