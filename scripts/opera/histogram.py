#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 14:46:04 2021

@author: bram
"""


import os
import gdal
import matplotlib.pyplot as plt
import numpy as np

def absoluteFilePaths(directory):
    for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f.endswith('tif'):
               yield os.path.join(dirpath, f)

def getArray(filename):
    ds = gdal.Open(filename)
    array = ds.GetRasterBand(1).ReadAsArray()
    return array

if __name__ == '__main__':
    
    qind_path = '/home/bram/Data/thesis/data_analysis/opera/3tiff_q_d/2015'

    qind_filenames = absoluteFilePaths(qind_path)

    result = []

    for cth_fn in qind_filenames:
        
        qind_array = getArray(cth_fn)
        
        for i in range(len(qind_array)):
            for j in range(len(qind_array[i])):
                
                qind = qind_array[i][j]
                
                if qind != -9999000:
                    
                    result.append(qind)
    
    bins = (np.array(range(0,102,2))/100).tolist()
    
    plt.hist(np.array(result), bins = bins) 
    plt.title("histogram") 
    plt.show()