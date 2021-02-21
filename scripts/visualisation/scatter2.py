#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 13:09:50 2020

"""

import os
import re
import gdal
import matplotlib.pyplot as plt

def absoluteFilePaths(directory, ext='tif'): 
    result = []
    for dirpath,_,filenames in os.walk(directory):
        for f in filenames:
            if f.endswith(ext):
                result.append(os.path.abspath(os.path.join(dirpath, f)))
    return result        
        
#msg_path = '/thesis/data_analysis/MSG/3align_opera/2015/cth'
#dwd_path = '/thesis/data_analysis/opera/3tiff_p_d/2015'
dwd_path = '/thesis/data_analysis/dwd/8alignMSG/2015'
msg_path = '/thesis/data_analysis/MSG/4TOV_MV/2015'

msg_filenames = absoluteFilePaths(msg_path)
dwd_filenames = absoluteFilePaths(dwd_path)

dwd_result = []
msg_result = []

for dwd_filename in dwd_filenames:
    
    date = re.search('002_[\d]{8}', dwd_filename).group()[4:]
    
    try:
        msg_filename = next(fn for fn in msg_filenames if date in fn)
    except StopIteration:
        continue
    
    dwd_ds = gdal.Open(dwd_filename)
    dwd_band = dwd_ds.GetRasterBand(1)
    dwd_array = dwd_band.ReadAsArray()
    
    msg_ds = gdal.Open(msg_filename)
    msg_band = msg_ds.GetRasterBand(1)
    msg_array = msg_band.ReadAsArray()
    
    for i in range(len(dwd_array)):
        for j in range(len(dwd_array[i])):
            if msg_array[i][j] > 0 and dwd_array[i][j] > 0.1:
                dwd_result.append(dwd_array[i][j])
                msg_result.append(msg_array[i][j])

from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Create plot
fig = plt.figure()
ax = fig.add_subplot(111)

data = ax.hist2d(msg_result, dwd_result, norm=LogNorm(), cmap = 'viridis', bins = 75, range = ([1, 14000], [1, 100]))

#ax.scatter(randomError, residuals, alpha=0.8, c=z, edgecolors='none', s=3)
#ax.plot(randomError, y_pred)

plt.xlabel('cloud top heigth [m above surface level]')
plt.ylabel('P DWD [mm]')
divider = make_axes_locatable(ax) #this and the following line are to make sure the colorbar is of same height as the image
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
cbar.minorticks_on()
cbar.ax.tick_params(labelsize=15)
plt.show()
