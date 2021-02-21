#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 13:09:50 2020

@author: bram
"""

import os
import re
import gdal
import matplotlib.pyplot as plt

def absoluteFilePaths(directory, ext): 
    result = []
    for dirpath,_,filenames in os.walk(directory):
        for f in filenames:
            if f.endswith(ext):
                result.append(os.path.abspath(os.path.join(dirpath, f)))
    return result        
        
random_error_path = '/data/thesis/data_analysis/imerg/4dail/2015/randomError'
residuals_path = '/data/thesis/data_analysis/residuals/1res_IMERG/2015'

random_error_filenames = absoluteFilePaths(random_error_path, 'tif')
residuals_filenames = absoluteFilePaths(residuals_path, 'tif')

res_list = []
random_error = []

for res_fn in residuals_filenames:
    
    date = re.search('DWD_[\d]{8}', res_fn).group()[4:]
    
    try:
        random_error_filename = next(fn for fn in random_error_filenames if date in fn)
    
    except StopIteration:
        continue
    
    res_ds = gdal.Open(res_fn)
    res_band = res_ds.GetRasterBand(1)
    res_array = res_band.ReadAsArray()
    
    random_error_ds = gdal.Open(random_error_filename)
    random_error_band = random_error_ds.GetRasterBand(1)
    random_error_array = random_error_band.ReadAsArray()
    
    for i in range(len(res_array)):
        for j in range(len(res_array[i])):
            if random_error_array[i][j] != -9999000 and res_array[i][j]!= -9999000 and (res_array[i][j] > 1 or res_array[i][j] < -1):
                res_list.append(res_array[i][j])
                random_error.append(random_error_array[i][j])

from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Create plot
fig = plt.figure()
ax = fig.add_subplot(111)

data = ax.hist2d(random_error, res_list, norm=LogNorm(), cmap = 'viridis',  cmin = 0.01, bins = 75)

#ax.scatter(random_error, res_list, alpha=0.8, edgecolors='none', s=3)
#ax.plot(randomError, y_pred)

plt.xlabel('random_error [mm]')
plt.ylabel('Residual [mm]')
divider = make_axes_locatable(ax) #this and the following line are to make sure the colorbar is of same height as the image
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
cbar.minorticks_on()
cbar.ax.tick_params(labelsize=15)
plt.show()