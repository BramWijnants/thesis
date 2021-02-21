#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 11:42:51 2021

@author: bram
"""
import os
import gdal
import re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

def absoluteFilePaths(directory):
    fns = []
    for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f.endswith('tif'):
               fns.append(os.path.join(dirpath, f))
    return fns

def getArray(filename):
    ds = gdal.Open(filename)
    array = ds.GetRasterBand(1).ReadAsArray()
    return array

def find_matching_days(path1, path2):
    result = {}
    
    file_paths1 = absoluteFilePaths(path1)
    file_paths2 = absoluteFilePaths(path2)

    for filename1 in file_paths1:
        date_string = re.search(r'20[\d]{6}', filename1).group()
        for filename2 in file_paths2:
            if date_string in filename2:
                result[date_string] = [filename1, filename2]
    return result

if __name__ == '__main__':
    

    residual_path = '/data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'
    qind_path = '/data/thesis/data_analysis/opera/3tiff_q_d/2015'
    
    res_qind_fns = find_matching_days(residual_path, qind_path)

    ress = []
    qinds = []
    
    ress_8 = []
    ress_2 = []
    
    qind_8 = []
    qinds_2 = []

    for date, (res_fn, qind_fn) in res_qind_fns.items():
        
        res_array = abs(getArray(res_fn))
        qind_array = getArray(qind_fn)
        
        mask = np.zeros(res_array.shape)
        mask[res_array == 9999000] = 1
        mask[qind_array == -9999000] = 1
        
        ress += res_array[mask == 0].tolist()
        qinds += qind_array[mask == 0].tolist()

    # Create plot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    #weights = np.ones_like(qinds) / len(qinds)
    
    data = ax.hist2d(qinds, ress, norm=LogNorm(), cmap = 'viridis',  bins = 100)
    
    #ax.scatter(randomError, residuals, alpha=0.8, c=z, edgecolors='none', s=3)
    #ax.plot(randomError, y_pred)
    
    plt.xlabel('Qind [mm]')
    plt.ylabel('Residual [mm]')
    divider = make_axes_locatable(ax) #this and the following line are to make sure the colorbar is of same height as the image
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
    cbar.minorticks_on()
    cbar.ax.tick_params(labelsize=15)
    plt.show()
    
    
    residual_path = '/data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'
    qind_path = '/data/thesis/data_analysis/opera/3tiff_q_d/2015'
    
    res_qind_fns = find_matching_days(residual_path, qind_path)
    
    counts_2 = {}
    counts_8 = {}
    ress_2 = list(range(0,101))
    ress_8 = list(range(0,101))
    
    for res in ress_2:
        counts_2[res]=0
        counts_8[res]=0

    for date, (res_fn, qind_fn) in res_qind_fns.items():
        
        res_array = abs(getArray(res_fn))
        qind_array = getArray(qind_fn)
        
        for i in range(len(res_array)):
            for j in range(len(qind_array)):
                
                ress = res_array[i][j]
                qind = qind_array[i][j]
                
                if ress != 9999000:
                    
                    if qind >= 0.19 and qind <= 0.21:
                        
                        counts_2[round(ress)] += 1
                        
                    elif qind >= 0.79 and qind <= 0.81:
                        
                        counts_8[round(ress)] += 1
    
    y_2 = []
    y_8 = []

    sum_2 = sum(list(counts_2.values()))
    sum_8 = sum(list(counts_8.values()))


    for y in counts_2.values():
        y_2.append(y/sum_2)

    for y in counts_8.values():
        y_8.append(y/sum_8)
        

    ress_2 = list(range(0,101))
    ress_8 = list(range(0,101))

    fig, ax = plt.subplots()
    
    ax.plot(ress_2,y_2)
    ax.plot(ress_8,y_8)
    plt.yscale('log')
    
    ax.set_xlabel('Qind')
    ax.set_ylabel('Frequency')
    
    plt.show()



    