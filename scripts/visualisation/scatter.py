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

def find_matching_days(path1, path2, path3, path4):
    result = {}
    
    file_paths1 = absoluteFilePaths(path1)
    file_paths2 = absoluteFilePaths(path2)
    file_paths3 = absoluteFilePaths(path3)
    file_paths4 = absoluteFilePaths(path4)

    for filename1 in file_paths1:
        date_string = re.search(r'20[\d]{6}', filename1).group()
        for filename2 in file_paths2:
            if date_string in filename2:
                for filename3 in file_paths3:
                    if date_string in filename3:
                        for filename4 in file_paths4:
                            if date_string in filename4:
                                result[date_string] = [filename1, filename2, filename3, filename4]
    return result

if __name__ == '__main__':
    
    error_path = '/data/thesis/data_analysis/imerg/4dail/2015/randomError'
    residual_path = '/data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'
    cth_path = '/data/thesis/data_analysis/MSG/3align_imerg/2015/cth'
    #cth_path ='/home/bram/Data/thesis/data_analysis/MSG/3align_opera/2015/cth'
    cth_path= '/data/thesis/data_analysis/MSG/4IMERG_tov_mv/2015'
    qind_path = '/data/thesis/data_analysis/opera/3tiff_q_d/2015'
    
    error_res_cth_fns = find_matching_days(error_path, residual_path, cth_path, qind_path)

    errors = []
    cths = []
    ress = []
    qinds = []

    cth = error = None

    for date, fns in error_res_cth_fns.items():
        
        error_fn, residual_fn, cth_path, qind_path = fns
        
        #cth_array = getArray(cth_path)
        #error_array = getArray(error_fn)
        res_array = getArray(residual_fn)
        qind_array = getArray(qind_path)
        
        for i in range(len(res_array)):
            for j in range(len(res_array[i])):
                
                #error = error_array[i][j]
                res = res_array[i][j]
                #cth = cth_array[i][j]
                qind = qind_array[i][j]
                
                if -9999000 not in [error, res, cth, qind]:
                    
                    ress.append(abs(res))
                    #errors.append(error)
                    #cths.append(cth)
                    qinds.append(qind)

    # Create plot
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    data = ax.hist2d(qinds, ress, norm=LogNorm(), cmap = 'viridis',  bins = 75)
    
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
     
    
    
    
    
    # Creating figure
    fig = plt.figure(figsize = (16, 9))
    ax = plt.axes(projection ="3d")
       
    # Add x, y gridlines 
    ax.grid(b = True, color ='grey', linestyle ='-.', linewidth = 0.3, alpha = 0.2) 
     
    # Creating color map
    my_cmap = plt.get_cmap('cubehelix')
     
    x = errors
    y = cths
    z = ress
    
    # Creating plot
    sctt = ax.scatter3D(x, y, z, alpha = 0.6,
                        c = (z), 
                        cmap = my_cmap, 
                        marker ='^')
     
    ax.set_xlabel('error', fontweight ='bold') 
    ax.set_ylabel('Elevation (AMSL)', fontweight ='bold') 
    ax.set_zlabel('Residual [mm]', fontweight ='bold')
    fig.colorbar(sctt, ax = ax, shrink = 0.5, aspect = 5)
     
    # show plot
    plt.show()

    error_path = '/data/thesis/data_analysis/imerg/4dail/2015/randomError'
    residual_path = '/data/thesis/data_analysis/residuals/1res_IMERG/2015'
    cth_path = '/data/thesis/data_analysis/MSG/3align_imerg/2015/cth'
    cth_path= '/data/thesis/data_analysis/MSG/4IMERG_tov_mv/2015'
    #cth_path ='/home/bram/Data/thesis/data_analysis/MSG/3align_opera/2015/cth'

    error_res_cth_fns = find_matching_days(error_path, residual_path, cth_path)

    errors = [[],[],[],[],[], []]

    for date, fns in error_res_cth_fns.items():
        
        error_fn, residual_fn, cth_path = fns
        
        cth_array = getArray(cth_path)
        error_array = getArray(error_fn)
        res_array = getArray(residual_fn)
        
        for i in range(len(error_array)):
            for j in range(len(error_array[i])):
                
                error = error_array[i][j]
                res = res_array[i][j]
                cth = cth_array[i][j]
                
                if error > 0 and res != -9999000 and cth != -9999000 and (res > 0.5 or res < -0.5):

                    if error <= 50:
                        errors[0].append((res, cth))                         

                    elif error <= 100:
                        errors[1].append((res, cth))
                    
                    elif error <= 150:
                        errors[2].append((res, cth))
                    
                    elif error <= 200:
                        errors[3].append((res, cth))
        
                    elif error <= 250:
                        errors[4].append((res, cth))

                    else:
                        errors[5].append((res, cth))

    y1 = [tuple_[0] for tuple_ in errors[0]]
    x1 = [tuple_[1] for tuple_ in errors[0]]
    
    y2 = [tuple_[0] for tuple_ in errors[1]]
    x2 = [tuple_[1] for tuple_ in errors[1]]
    
    y3 = [tuple_[0] for tuple_ in errors[2]]
    x3 = [tuple_[1] for tuple_ in errors[2]]
    
    y4 = [tuple_[0] for tuple_ in errors[3]]
    x4 = [tuple_[1] for tuple_ in errors[3]]
    
    y5 = [tuple_[0] for tuple_ in errors[4]]
    x5 = [tuple_[1] for tuple_ in errors[4]]
    
    y6 = [tuple_[0] for tuple_ in errors[5]]
    x6 = [tuple_[1] for tuple_ in errors[5]]
    
    # Plot
   # plt.scatter(x1, y1, alpha=0.5)
    #plt.title('Scatter plot pythonspot.com')
    #plt.xlabel('x')
    #plt.ylabel('y')
    #plt.show()
    
    x = [x1, x2, x3, x4, x5, x6]
    y = [y1, y2, y3, y4, y5, y6]
    

    
    fig, ax = plt.subplots(2, 3, sharex='col', sharey='row')
    
    titles = [(0, 50), (50, 100), (100,150), (150,200),(200,250), (250, 400)]
    count = 0
    
    for i in range(2):
        for j in range(3):
            

            data = ax[i, j].hist2d(x[count], y[count], cmap = 'viridis', cmin=1, bins = 75,range=([0, 14000], [-50, 100]))
            ax[i,j].grid(True, linewidth=0.5, color='grey', linestyle='-')
            ax[i,j].plot(14000*[0], linewidth=0.7, color='black')
            # set the y-spine
           # ax[i,j].spines['bottom'].set_position('zero')
            
            ax[i,j].xaxis.set_ticks_position('bottom')            
            
            divider = make_axes_locatable(ax[i,j]) #this and the following line are to make sure the colorbar is of same height as the image
            cax = divider.append_axes("right", size="5%", pad=0.05)
            cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
            #cbar.minorticks_on()
            #cbar.ax.tick_params(labelsize=15)


            ax[i,j].set_title('{} <= error < {}'.format(titles[count][0], titles[count][1]))
            count += 1
            
            if i == 1:
                ax[i,j].set(xlabel = 'CTH [m above surface]', ylabel = 'Residual [mm]')
            
            if (i,j) == (0,0):
                ax[i,j].set(ylabel = 'Residual [mm]')
                
    fig.show() 
    

    
    from matplotlib.colors import LogNorm
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    
    # Create plot
    fig = plt.figure()
    ax = fig.add_subplot(121)
    
    data = ax.hist2d(x1, y1, cmap = 'viridis', norm=LogNorm(), bins = 75,range=([0, 2500], [-50, 100]))
    
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