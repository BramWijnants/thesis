#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 11:42:51 2021

@author: bram
"""

import os
import gdal
import re
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
                result[date_string] = (filename1, filename2)
    return result

if __name__ == '__main__':
    
    residual_path = '/home/bram/Data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'
    qind_path = '/home/bram/Data/thesis/data_analysis/opera/3tiff_q_d/2015'
    dem_path = '/home/bram/Data/thesis/data_analysis/dem/srtm_germany_dsm_aligned_opera.tif'

    dem_array = getArray(dem_path)
    qind_res_fns = find_matching_days(qind_path, residual_path)

    qinds = []
    dem = []
    ress = []

    for date, fns in qind_res_fns.items():
        
        qind_fn, residual_fn = fns
        qind_array = getArray(qind_fn)
        res_array = getArray(residual_fn)
        
        for i in range(len(qind_array)):
            for j in range(len(qind_array[i])-1):
                
                qind = qind_array[i][j]
                res = res_array[i][j]
                
                if qind != -9999000 and res != -9999000:
                    
                    ress.append(res)
                    qinds.append(qind)
                    dem.append(dem_array[i][j])

    # Create plot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    data = ax.hist2d(qinds, dem, norm=LogNorm(), cmap = 'viridis',  bins = 75)
    
    #ax.scatter(randomError, residuals, alpha=0.8, c=z, edgecolors='none', s=3)
    #ax.plot(randomError, y_pred)
    
    plt.xlabel('OPERA Quality Index')
    plt.ylabel('Elevation (AMSL)')
    divider = make_axes_locatable(ax) #this and the following line are to make sure the colorbar is of same height as the image
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
    cbar.minorticks_on()
    cbar.ax.tick_params(labelsize=15)
    plt.show()
     
    # Creating figure
    fig = plt.figure(figsize = (16, 9))
    ax = plt.axes(projection ="3d")
       
    # Add x, y gridlines 
    ax.grid(b = True, color ='grey', linestyle ='-.', linewidth = 0.3, alpha = 0.2) 
     
    # Creating color map
    my_cmap = plt.get_cmap('cubehelix')
     
    x = qinds
    y = dem
    z = ress
    
    # Creating plot
    sctt = ax.scatter3D(x, y, z, alpha = 0.6,
                        c = (z), 
                        cmap = my_cmap, 
                        marker ='^')
     
    ax.set_xlabel('Qind', fontweight ='bold') 
    ax.set_ylabel('Elevation (AMSL)', fontweight ='bold') 
    ax.set_zlabel('Residual [mm]', fontweight ='bold')
    fig.colorbar(sctt, ax = ax, shrink = 0.5, aspect = 5)
     
    # show plot
    plt.show()

    residual_path = '/home/bram/Data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'
    qind_path = '/home/bram/Data/thesis/data_analysis/opera/3tiff_q_d/2015'
    dem_path = '/home/bram/Data/thesis/data_analysis/dem/srtm_germany_dsm_aligned_opera.tif'

    dem_array = getArray(dem_path)
    qind_res_fns = find_matching_days(qind_path, residual_path)

    qinds = [[],[],[],[],[]]
    dem = []
    ress = []

    for date, fns in qind_res_fns.items():
        
        qind_fn, residual_fn = fns
        qind_array = getArray(qind_fn)
        res_array = getArray(residual_fn)
        
        for i in range(len(qind_array)):
            for j in range(len(qind_array[i])-1):
                
                qind = qind_array[i][j]
                res = res_array[i][j]
                
                if qind != -9999000 and res != -9999000:

                    if qind <= 0.2:
                        qinds[0].append((res, dem_array[i][j]))
                    
                    elif qind <= 0.4:
                        qinds[1].append((res, dem_array[i][j]))
                    
                    elif qind <= 0.6:
                        qinds[2].append((res, dem_array[i][j]))
        
                    elif qind <= 0.8:
                        qinds[3].append((res, dem_array[i][j]))
                        
                    elif qind <= 1:
                        qinds[4].append((res, dem_array[i][j]))                        
             
                        
    y1 = [tuple_[0] for tuple_ in qinds[0]]
    x1 = [tuple_[1] for tuple_ in qinds[0]]
    
    y2 = [tuple_[0] for tuple_ in qinds[1]]
    x2 = [tuple_[1] for tuple_ in qinds[1]]
    
    y3 = [tuple_[0] for tuple_ in qinds[2]]
    x3 = [tuple_[1] for tuple_ in qinds[2]]
    
    y4 = [tuple_[0] for tuple_ in qinds[3]]
    x4 = [tuple_[1] for tuple_ in qinds[3]]
    
    y5 = [tuple_[0] for tuple_ in qinds[4]]
    x5 = [tuple_[1] for tuple_ in qinds[4]]
    
    # Plot
   # plt.scatter(x1, y1, alpha=0.5)
    #plt.title('Scatter plot pythonspot.com')
    #plt.xlabel('x')
    #plt.ylabel('y')
    #plt.show()
    
    x = [x1, x2, x3, x4, x5]
    y = [y1, y2, y3, y4, y5]
    
    fig, ax = plt.subplots(2, 3, sharex='col', sharey='row')
    
    count = 0
    
    for i in range(2):
        for j in range(3):
            data = ax[i, j].hist2d(x[count], y[count], cmap = 'viridis', norm=LogNorm(), bins = 75,range=([0, 2500], [-100, 100]))
            count += 1
            if count == 5:
                break
    
    titles = [(0, 0.2), (0.2, 0.4), (0.4,0.6), (0.6,0.8),(0.8,1)]
    
    for i, adsfa in enumerate(ax.flat[:-1]):
        adsfa.set(xlabel = 'Elevation [ m AMSL]', ylabel = 'Residual [mm]')
        adsfa.set_title('{} <= Qind < {}'.format(titles[i][0], titles[i][1]))
    
    for ax in ax.flat:
        ax.label_outer()
    
    divider = make_axes_locatable(ax) #this and the following line are to make sure the colorbar is of same height as the image
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
    cbar.minorticks_on()
    cbar.ax.tick_params(labelsize=15)
   
    fig.show()
    

    
    from matplotlib.colors import LogNorm
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    
    # Create plot
    fig = plt.figure()
    ax = fig.add_subplot(121)
    
    data = ax.hist2d(x1, y1, cmap = 'viridis', norm=LogNorm(), bins = 75,range=([0, 2500], [-100, 100]))
    
    #ax.scatter(randomError, residuals, alpha=0.8, c=z, edgecolors='none', s=3)
    #ax.plot(randomError, y_pred)
    
#    plt.xlabel('Elevation (AMSL)')
#    plt.ylabel('Residual [mm]')
#    divider = make_axes_locatable(ax) #this and the following line are to make sure the colorbar is of same height as the image
#    cax = divider.append_axes("right", size="5%", pad=0.05)
#    cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
#    cbar.minorticks_on()
#    cbar.ax.tick_params(labelsize=15)


    ax2 = fig.add_subplot(122)
    
    data2 = ax2.hist2d(x2, y2, cmap = 'viridis', norm=LogNorm(), bins = 75,range=([0, 2500], [-100, 100]))
    
    #ax.scatter(randomError, residuals, alpha=0.8, c=z, edgecolors='none', s=3)
    #ax.plot(randomError, y_pred)
    
#    divider2 = make_axes_locatable(ax2) #this and the following line are to make sure the colorbar is of same height as the image
#    cax2 = divider2.append_axes("right", size="5%", pad=0.05)
#    cbar2 = plt.colorbar(data2[3], cax = cax2)#use data[3] because hist2d returns a tuple, the [3] selects the image 
#    cbar2.minorticks_on()
#    cbar2.ax.tick_params(labelsize=15)

    ax3 = fig.add_subplot(221)
    
    data3 = ax3.hist2d(x3, y3, cmap = 'viridis', norm=LogNorm(), bins = 75,range=([0, 2500], [-100, 100]))
    
    #ax.scatter(randomError, residuals, alpha=0.8, c=z, edgecolors='none', s=3)
    #ax.plot(randomError, y_pred)

    ax4 = fig.add_subplot(222)
    
    data4 = ax4.hist2d(x4, y4, cmap = 'viridis', norm=LogNorm(), bins = 75,range=([0, 2500], [-100, 100]))
    
    #ax.scatter(randomError, residuals, alpha=0.8, c=z, edgecolors='none', s=3)
    #ax.plot(randomError, y_pred)
    
    divider4 = make_axes_locatable(ax4) #this and the following line are to make sure the colorbar is of same height as the image
    cax4 = divider4.append_axes("right", size="5%", pad=0.05)
    cbar4 = plt.colorbar(data4[3], cax = cax4)#use data[3] because hist2d returns a tuple, the [3] selects the image 
    cbar4.minorticks_on()
    cbar4.ax.tick_params(labelsize=15)
    plt.show()