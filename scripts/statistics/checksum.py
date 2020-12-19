#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 13:54:43 2020

"""
import gdal
import os
import numpy as np

def absoluteFilePaths(directory): 
   result = []
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f[-3:] == 'tif':
               result.append(os.path.abspath(os.path.join(dirpath, f)))     
   return result

def calculateSingleResiduals(input_file, threshold = 0):
    residual_list =[]
    ds = gdal.Open(input_file)
    array = ds.GetRasterBand(1).ReadAsArray()
    for i in range(len(array)):
        for j in range(len(array[i])):
            pixel_value = array[i][j]
            if pixel_value != -9999000 and pixel_value > threshold:
                residual_list.append(array[i][j])
    return residual_list

def calculateResiduals(input_folder, threshold = 0):
    residual_list = []
    filename_generator = absoluteFilePaths(input_folder)
    for filename_residual_map in filename_generator:
        residual_list += calculateSingleResiduals(filename_residual_map, threshold)
    return residual_list
    
def calculateAbsoluteResiduals(input_folder):
    residuals_list = []
    filename_generator = absoluteFilePaths(input_folder)
    for filename_residual_map in filename_generator:
        ds = gdal.Open(filename_residual_map)
        array = ds.GetRasterBand(1).ReadAsArray()
        for i in range(len(array)):
            for j in range(len(array[i])):
                abs_pixel_value = abs(array[i][j])
                if abs_pixel_value != 9999000:
                    residuals_list.append(abs_pixel_value)
        ds.FlushCache()
    return residuals_list


#****************************************************************************#
#*                               * M * A * I * N *                          *#
#****************************************************************************#

input_folder_OPERA = '/thesis/data_analysis/opera/2tiff_p/2015'

filenames = absoluteFilePaths(input_folder_OPERA)

sumation = []

for i, filename in enumerate(filenames): # add count 2darray
    
    ds = gdal.Open(filename)
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray()
    mx = np.ma.masked_values(array, -9999000)

    mask_arr = np.ma.masked_where(mx < 0, mx) 

    filesum = mask_arr.sum()

    sumation.append((filename, filesum))
    
def take_second(elem):
    return elem[1]

hello = sorted(sumation, key = take_second)

