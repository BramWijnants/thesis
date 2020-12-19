#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 11:20:02 2020

"""
#make a densiy scatterplot for 30 min time resolution (because of gaps) for the four different seasons
#on the y-axis the difference (IMERG-radar) rainfall depth is plotted, on the x-axis the radar rainfall depth
#furthermore, the amount of observations shown in the subfigures 
#used to created figure 4 of the IMERG manuscript

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colors import LogNorm
import glob

#-----------------
#settings
#-----------------

threshold = 0.1 #0.0 change sign!
onlyRadarThreshold = True #False
#if True, the minimum threshold is only applied to the radar estimates. 
#If false, the threshold is also applied to the IMERG estimates. 
iYear = 'All'
saveName = 'fig_04.png' #'fig_04_both_above_0.1.png'.format(threshold)
sameColorbar = False

#-----------------
#functions
#-----------------
def makeThresholdPairs(IMERGData,radarData,thresholdValue,onlyRadarThreshold):
    #Make paired estimates between radar and IMERG 
    #both IMERGdata and radarData need to be numpy dataset. 
    #The threshold values are on top of scripts below settings, and are given as arguments for the function
    
    listDiff = []
    listRadar = []
    if np.shape(IMERGData)==np.shape(radarData):
        #only perform calculations if the shapes of the reference and satellite products are similar 
        for iTime in range(len(IMERGData)):
            for iLat in range(len(IMERGData[0])):
                for iLon in range(len(IMERGData[0][0])):
                    if onlyRadarThreshold:
                        if radarData[iTime][iLat][iLon] < thresholdValue or np.isnan(radarData[iTime][iLat][iLon]) or np.isnan(IMERGData[iTime][iLat][iLon]):
                            continue
                    else:
                        if np.isnan(radarData[iTime][iLat][iLon]) or np.isnan(IMERGData[iTime][iLat][iLon]) or radarData[iTime][iLat][iLon] < thresholdValue or IMERGData[iTime][iLat][iLon] < thresholdValue:
                            continue
                    
                    #only values > threshold for radar (and IMERG if onlyRadarThreshold is false) and which are not-nan are selected    
                        
                    listDiff.append(IMERGData[iTime][iLat][iLon]-radarData[iTime][iLat][iLon])
                    listRadar.append(radarData[iTime][iLat][iLon])

    return np.array(listDiff),np.array(listRadar)

#-----------------
#read in data and loop
#-----------------

seasons = ['DJF','MAM','JJA','SON']

fig, ax = plt.subplots(2,2)
axes = [ax[0,0],ax[0,1],ax[1,0],ax[1,1]]
fig.set_size_inches(12, 12)

for iSeas in range(len(seasons)):   
    if iYear == 'All':
        precipRadarRead = xr.open_mfdataset(glob.glob('../process/seasonal_spatial_data/{}/RAD_NL25_REGRID_EM_30min_*_{}.V06B.HDF5.nc4'.format(seasons[iSeas],seasons[iSeas])))
        precipIMERGLate = xr.open_mfdataset(glob.glob('../process/seasonal_spatial_data/{}/3B-HHR-L.MS.MRG.3IMERG.*_{}.V06B.HDF5.nc4'.format(seasons[iSeas],seasons[iSeas])))        

    else:
        precipRadarRead = xr.open_dataset('../process/seasonal_spatial_data/{}/RAD_NL25_REGRID_EM_30min_{}_{}.V06B.HDF5.nc4'.format(seasons[iSeas],iYear,seasons[iSeas]))
        precipIMERGLate = xr.open_dataset('../process/seasonal_spatial_data/{}/3B-HHR-L.MS.MRG.3IMERG.{}_{}.V06B.HDF5.nc4'.format(seasons[iSeas],iYear,seasons[iSeas]))
    
    valuesIMERG = precipIMERGLate['precipitationUncal'].values
    valuesRadar = precipRadarRead['precipitation'].values

    listDiff, listRadar = makeThresholdPairs(valuesIMERG,valuesRadar,threshold,onlyRadarThreshold)
    maxValue = 50
    text = "n = {}".format(len(listDiff),threshold)

    axes[iSeas].hlines(y=0, xmin = 0, xmax = 30, colors = 'black', linewidth = 1.2)
    data = axes[iSeas].hist2d(listRadar,listDiff, cmap = 'viridis', norm = LogNorm(), bins = 75, range = ([0, maxValue], [-25, maxValue]))
    axes[iSeas].set_ylim(-25,45)
    axes[iSeas].set_xlim(0,27)
    if iSeas == 2 or iSeas == 3:
        axes[iSeas].set_xlabel('30-min radar rainfall depth [mm]', fontsize = 16)
    if iSeas == 0 or iSeas == 2:
        axes[iSeas].set_ylabel('difference (IMERG - radar) [mm]', fontsize = 16)
    axes[iSeas].set_title('{}'.format(seasons[iSeas]), fontsize = 17)
    axes[iSeas].grid(True)
    axes[iSeas].text(15,40, text, va='top', ha='left', wrap=True, fontsize=15)
#    axes[iSeas].set_aspect('equal') #make plot square
    for tick in axes[iSeas].xaxis.get_major_ticks():
        tick.label.set_fontsize(15) #change size ticks
    for tick in axes[iSeas].yaxis.get_major_ticks():
        tick.label.set_fontsize(15)
    if sameColorbar:
        data[3].set_clim(1, 550000)
    if iSeas == 0 or iSeas == 1:
        axes[iSeas].set_xticklabels([])
    if iSeas == 1 or iSeas == 3:
        axes[iSeas].set_yticklabels([])
    divider = make_axes_locatable(axes[iSeas]) #this and the following line are to make sure the colorbar is of same height as the image
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
    cbar.minorticks_on()
    cbar.ax.tick_params(labelsize=15)
    
    
#if iYear == 'All':
#    ax[0,0].set_title('{}, 2015-2019'.format(seasons[0]), fontsize = 15)
#else:
#    ax[0,0].set_title('{}-{}'.format(iYear,seasons[0]), fontsize = 15)
fig.subplots_adjust(wspace=0.18, hspace=0.13)
plt.savefig(saveName, dpi=500,
    bbox_inches='tight')
plt.show()


