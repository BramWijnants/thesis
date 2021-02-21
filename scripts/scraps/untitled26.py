#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 12:41:54 2021

@author: bram
"""
import os
import gdal
import re
import numpy as np


def absoluteFilePaths(directory): 
   result = []
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f[-3:] == 'tif':
               result.append(os.path.abspath(os.path.join(dirpath, f)))     
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

def relative_bias_categorized(filename_dict):
    
    residuals = [[] for _ in range(6)]
    references = [[] for _ in range(6)]
    biases = [[] for _ in range(6)]

    for _, filenames in filename_dict.items():

        fn_ref, fn_res, fn_error = filenames

        ds_ref = gdal.Open(fn_ref)
        band_ref = ds_ref.GetRasterBand(1)
        array_ref = band_ref.ReadAsArray()

        ds_res = gdal.Open(fn_res)
        band_res = ds_res.GetRasterBand(1)
        array_res = band_res.ReadAsArray()

        ds_error = gdal.Open(fn_error)
        band_error = ds_error.GetRasterBand(1)
        array_error = band_error.ReadAsArray()

        for i in range(len(array_ref)):
            for j in range(len(array_ref[i])):
                
                ref = array_ref[i][j]
                res = array_res[i][j]
                error = array_error[i][j]
                
                if error != -9999000 and res != -9999000 and ref != -9999000:

                    if error <= 50:
                        residuals[0].append(res)    
                        references[0].append(ref)

                    elif error <= 100:
                        residuals[1].append(res)    
                        references[1].append(ref)
                    
                    elif error <= 150:
                        residuals[2].append(res)    
                        references[2].append(ref)
                    
                    elif error <= 200:
                        residuals[3].append(res)    
                        references[3].append(ref)
                        
                    elif error <= 250:
                        residuals[4].append(res)    
                        references[4].append(ref)

                    else:
                        residuals[5].append(res)    
                        references[5].append(ref)              
    
    ress = []
    refs = []
    
    for i in range(len(residuals)):
        biases[i] = sum(residuals[i])/sum(references[i])
        ress.append(sum(residuals[i]))
        refs.append(sum(references[i]))
    
    return refs , ress

if __name__ == '__main__':

    REF_PATH = '/data/thesis/data_analysis/dwd/6alignIMERG/2015'
    #REF_PATH = '/data/thesis/data_analysis/dwd/7alignOPERA/2015'
    IMERG_PATH = '/data/thesis/data_analysis/imerg/4dail/2015/precipitationCal'
    #IMERG_PATH = '/data/thesis/data_analysis/imerg/5aligned_opera/2015/precipitationCal'
    #IMERG_PATH = '/data/thesis/data_analysis/imerg/5aligned_opera_spline/2015/precipitationCal'
    #RES_IMERG_PATH = '/data/thesis/data_analysis/residuals/1res_IMERG_splined/2015'
    RES_IMERG_PATH = '/data/thesis/data_analysis/residuals/1res_IMERG/2015'
    #RES_IMERG_PATH = '/data/thesis/data_analysis/residuals/1res_IMERG_aligned/2015'
    
    ERROR_IMERG_PATH = '/data/thesis/data_analysis/imerg/4dail/2015/randomError'

    fn_dict = find_matching_days(path1=REF_PATH, path2=RES_IMERG_PATH, path3=ERROR_IMERG_PATH)
    residuals, references = relative_bias_categorized(fn_dict)
    
    #print('\n'+10*'-'+'IMERG'+'-'*10+'\nFAR: {}\nPOD: {}\nRMSE: {}\nRel Bias: {}'.format(round(FAR_thingy,3), round(POD_thingy,3), round(RMSE_thingy,3), round(BIAS_thingy, 3)))
    

    
    
    