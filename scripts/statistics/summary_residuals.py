#!/usr/bin/env python3
"""
Created on Mon Oct 26 12:53:49 2020

@author: bram
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import re
import time
import gdal

def absoluteFilePaths(directory): 
   result = []
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f[-3:] == 'tif':
               result.append(os.path.abspath(os.path.join(dirpath, f)))     
   return result

def calculateSingleResiduals(input_file):
    residual_list =[]
    ds = gdal.Open(input_file)
    array = ds.GetRasterBand(1).ReadAsArray()
    for i in range(len(array)):
        for j in range(len(array[i])):
            pixel_value = array[i][j]
            if pixel_value != -9999000:
                residual_list.append(array[i][j])
    return residual_list

def calculateResiduals(input_folder):
    residual_list = []
    filename_generator = absoluteFilePaths(input_folder)
    for filename_residual_map in filename_generator:
        residual_list += calculateSingleResiduals(filename_residual_map)
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

input_folder_IMERG = '/data/thesis/data_analysis/residuals/1res_IMERG/2015'
input_folder_OPERA = '/data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'


##############################################################################
###                          YEARLY IMERG HISTOGRAM                        ###
##############################################################################

residuals_IMERG = np.array(calculateResiduals(input_folder_IMERG))

fig, (ax1, ax2) = plt.subplots(1,2)
fig.suptitle('IMERG residuals 2015')
ax1.set_ylabel('Frequency')
ax1.set_xlabel('Residual [mm]')
ax1.hist(residuals_IMERG, log = False, color = "rosybrown", rwidth=0.9)

ax2.set_ylabel('Frequency')
ax2.set_xlabel('Residual [mm]')
ax2.hist(residuals_IMERG, bins=list(range(-150,200,10)),log = True, color = "rosybrown", rwidth=0.9)
plt.show()

absolute_residuals_IMERG = np.array(calculateAbsoluteResiduals(input_folder_IMERG))

fig, (ax1, ax2) = plt.subplots(1,2)
fig.suptitle('IMERG absolute residuals 2015')
ax1.set_ylabel('Frequency')
ax1.set_xlabel('Absolute residual [mm]')
ax1.hist(absolute_residuals_IMERG, bins=list(range(0,200,10)),log = False, color = "rosybrown", rwidth=0.9)

ax2.set_ylabel('Frequency')
ax2.set_xlabel('Absolute residual [mm]')
ax2.hist(absolute_residuals_IMERG, bins=list(range(0,200,10)),log = True, color = "rosybrown", rwidth=0.9)
plt.show()


##############################################################################
###                          YEARLY OPERA HISTOGRAM                        ###
##############################################################################

residuals_OPERA = np.array(calculateResiduals(input_folder_OPERA))

fig, (ax1, ax2) = plt.subplots(1,2)
fig.suptitle('OPERA residuals 2015')
ax1.set_ylabel('Frequency')
ax1.set_xlabel('Residual [mm]')
ax1.hist(residuals_OPERA, bins=list(range(-30,30,5)),log = False, color = "rosybrown")

ax2.set_ylabel('Frequency')
ax2.set_xlabel('Residual [mm]')
ax2.hist(residuals_OPERA, bins=list(range(-200,200,20)),log = True, color = "rosybrown")
plt.show()

absolute_residuals_OPERA = np.array(calculateAbsoluteResiduals(input_folder_OPERA))

fig, (ax1, ax2) = plt.subplots(1,2)
fig.suptitle('OPERA absolute residuals 2015')
ax1.set_ylabel('Frequency')
ax1.set_xlabel('Absolute residual [mm]')
ax1.hist(absolute_residuals_OPERA, bins=list(range(0,40,5)),log = False, color = "rosybrown")

ax2.set_ylabel('Frequency')
ax2.set_xlabel('Absolute residual [mm]')
ax2.hist(absolute_residuals_OPERA, bins=list(range(0,2200,100)),log = True, color = "rosybrown")
plt.show()


##############################################################################
###                        MONTHLY  IMERG  BOXPLOTS                        ###
##############################################################################

filenames = absoluteFilePaths(input_folder_IMERG)
residuals = []

for i in range(1,13):
    month_string = str(i).zfill(2)
    monthly_residuals = None
    for filename in filenames:
        month_file = re.search('DWD_20[\d]{6}', filename).group()[8:-2]
        if month_file == month_string:
            daily_residuals = calculateSingleResiduals(filename)
            
            if monthly_residuals is None:
                monthly_residuals = np.array(daily_residuals)
                
            else:    
                monthly_residuals = np.append(monthly_residuals, np.array(daily_residuals))
                
    residuals.append(monthly_residuals)

labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep','Oct' ,'Nov','Dec']

fig = plt.figure() 
ax = fig.add_subplot()
ax.boxplot(np.array(residuals), labels=labels, showfliers=False) 
ax.set_ylabel('IMERG Residual [mm]')
plt.show() 


##############################################################################
###                          MONTHLY OPERA BOXPLOTS                        ###
##############################################################################

filenames = absoluteFilePaths(input_folder_OPERA)
residuals = []

for i in range(1,13):
    month_string = str(i).zfill(2)
    monthly_residuals = []
    for filename in filenames:
        month_file = re.search('DWD_20[\d]{6}', filename).group()[8:-2]
        if month_file == month_string:
            daily_residuals = calculateSingleResiduals(filename)
            monthly_residuals += daily_residuals
    residuals.append(monthly_residuals)

fig = plt.figure() 
ax = fig.add_subplot()
bp = ax.boxplot(residuals, showfliers=False, labels = labels) 
ax.set_ylabel('Residual OPERA [mm]')
plt.show() 


##############################################################################
###                            IMERG / OPERA RESIDUAL MAP                  ###
##############################################################################

"""                              Y E A R L Y                               """

output_folder = '/data/thesis/data_analysis/residuals/output'
filenames = absoluteFilePaths(input_folder_IMERG)

ds = gdal.Open(filenames[0])
band = ds.GetRasterBand(1)
array = band.ReadAsArray()
mx = np.ma.masked_values(array, -9999000)
count = np.zeros(array.shape)
count[mx.mask == False] = 1

for i, filename in enumerate(filenames[1:]):
    
    ds2 = gdal.Open(filenames[0])
    band2 = ds.GetRasterBand(1)
    array2 = band.ReadAsArray()
    mx2 = np.ma.masked_values(array2, -9999000)

    mx += mx2
    count[mx2.mask == False] += 1

#mx /= count

year = re.search('/[\d]{4}/', filename).group().strip('/')
output_fn = 'Yearly_PCal_IMERG_{}.tif'.format(year)
full_output_fn = os.path.join(output_folder, output_fn)
    
#save
driver = gdal.GetDriverByName('GTiff')
dst_ds = driver.CreateCopy(full_output_fn, ds)

dst_band = dst_ds.GetRasterBand(1)
dst_band.WriteArray(mx.filled())
dst_band.ComputeStatistics(True)
    
ds.FlushCache()
ds2.FlushCache()
dst_ds.FlushCache()

"""                             M O N T H L Y                              """

output_folder = '/home/bram/studie/thesis/data_analysis/residuals/output/monthly_IMERG'
filenames = absoluteFilePaths(input_folder_IMERG)
ds=None

for i in range(1,13):
    month_string = str(i).zfill(2)
    for filename in filenames:
        month_file = re.search('DWD_20[\d]{6}', filename).group()[8:-2]
        if month_file == month_string:
            
            if ds == None:
                ds = gdal.Open(filename)
                band = ds.GetRasterBand(1)
                array = band.ReadAsArray()
                mx = abs(np.ma.masked_values(array, -9999000))
                count = np.zeros(array.shape)
                count[mx.mask == False] = 1
            
            else:
                ds2 = gdal.Open(filename)
                band2 = ds.GetRasterBand(1)
                array2 = band.ReadAsArray()
                mx2 = abs(np.ma.masked_values(array2, -9999000))
            
                mx += mx2
                count[mx2.mask == False] += 1
            
    mx /= count
    
    year = re.search('/[\d]{4}/', filename).group().strip('/')
    output_fn = 'Monthly_residuals_IMERG-DWD_{}{}.tif'.format(year, month_string)
    full_output_fn = os.path.join(output_folder, output_fn)
    
    #save
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.CreateCopy(full_output_fn, ds)

    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(mx.filled())
    dst_band.ComputeStatistics(True)
    
    ds.FlushCache()
    ds2.FlushCache()
    dst_ds.FlushCache()
    ds = None
            

##############################################################################
###                            OPERA RESIDUAL MAP                          ###
##############################################################################

"""                              Y E A R L Y                               """

output_folder = '/home/bram/studie/thesis/data_analysis/residuals/output'
filenames = absoluteFilePaths(input_folder_OPERA)

ds = gdal.Open(filenames[0])
band = ds.GetRasterBand(1)
array = band.ReadAsArray()
mx = np.ma.masked_values(array, -9999000)#.__abs__()
count = np.zeros(array.shape)
count[mx.mask == False] = 1

for i, filename in enumerate(filenames[1:]): # add count 2darray

    ds2 = gdal.Open(filenames[0])
    band2 = ds.GetRasterBand(1)
    array2 = band.ReadAsArray()
    mx2 = np.ma.masked_values(array2, -9999000)#.__abs__()

    mx += mx2
    count[mx2.mask == False] += 1

mx /= count

year = re.search('/[\d]{4}/', filename).group().strip('/')
output_fn = 'Yearly_abs_residuals_OPERA-DWD_{}.tif'.format(year)
full_output_fn = os.path.join(output_folder, output_fn)

#save
driver = gdal.GetDriverByName('GTiff')
dst_ds = driver.CreateCopy(full_output_fn, ds)

dst_band = dst_ds.GetRasterBand(1)
dst_band.WriteArray(mx.filled())
dst_band.ComputeStatistics(True)

ds.FlushCache()
ds2.FlushCache()
dst_ds.FlushCache()


##############################################################################
###                          IMERG RESIDUAL SCATTER PLOT                   ###
##############################################################################

IMERG_residual_path = '/home/bram/studie/thesis/data_analysis/residuals/1res_IMERG/2015'
IMERG_QIND_path = '/home/bram/studie/thesis/data_analysis/imerg/4dail/2015/precipitationQualityIndex'

filenames_residuals = absoluteFilePaths(IMERG_residual_path)
filenames_QIND = absoluteFilePaths(IMERG_QIND_path)

residuals = []
QINDS = []

for filename_res in filenames_residuals:
    
    date_string_res = re.search('DWD_20[\d]{6}', filename_res).group()[4:]
    date_res = time.strptime(date_string_res, '%Y%m%d')
    
    ds_res = gdal.Open(filename_res)
    band_res = ds_res.GetRasterBand(1)
    array_res = band_res.ReadAsArray()
        
    for filename_QIND in filenames_QIND:
        
        date_string_QIND = re.search('ERG.20[\d]{6}', filename_QIND).group()[4:]
        date_QIND = time.strptime(date_string_QIND, '%Y%m%d')
        
        if date_res == date_QIND:
        
            ds_QIND = gdal.Open(filename_QIND)
            band_QIND = ds_QIND.GetRasterBand(1)
            array_QIND = band_QIND.ReadAsArray()
            
            for i in range(len(array_res)):
                for j in range(len(array_res[i])):
                    
                    value_res = array_res[i][j]
                    value_QIND = array_QIND[i][j]
                    
                    if value_res != -9999000 and value_QIND != -9999000:
                        
                        residuals.append(abs(value_res))
                        QINDS.append(value_QIND)



from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Create plot
fig = plt.figure()
ax = fig.add_subplot(111)
data = ax.hist2d(QINDS, residuals, cmap = 'viridis',norm = LogNorm(), bins = 75)

#ax.scatter(randomError, residuals, alpha=0.8, c=z, edgecolors='none', s=3)
#ax.plot(randomError, y_pred)

plt.xlabel('QIND_IMERG')
plt.ylabel('Absolute residuals')
divider = make_axes_locatable(ax) #this and the following line are to make sure the colorbar is of same height as the image
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
cbar.minorticks_on()
cbar.ax.tick_params(labelsize=15)
plt.show()


##############################################################################
###                          IMERG RESIDUAL SCATTER PLOT  QIND STUFF       ###
##############################################################################

IMERG_residual_path = '/home/bram/studie/thesis/data_analysis/residuals/1res_IMERG/2015'
IMERG_QIND_path = '/home/bram/studie/thesis/data_analysis/imerg/4dail/2015/precipitationQualityIndex'
IMERG_randomError_path = '/home/bram/studie/thesis/data_analysis/imerg/4dail/2015/randomError'

filenames_residuals = absoluteFilePaths(IMERG_residual_path)
filenames_QIND = absoluteFilePaths(IMERG_QIND_path)
filenames_randomError = absoluteFilePaths(IMERG_randomError_path)

low_randomError = []
high_randomError = []

low_res = []
high_res = []

for filename_res in filenames_residuals:
    
    date_string_res = re.search('DWD_20[\d]{6}', filename_res).group()[4:]
    date_res = time.strptime(date_string_res, '%Y%m%d')
    
    ds_res = gdal.Open(filename_res)
    band_res = ds_res.GetRasterBand(1)
    array_res = band_res.ReadAsArray()
        
    for filename_QIND in filenames_QIND:
        
        date_string_QIND = re.search('ERG.20[\d]{6}', filename_QIND).group()[4:]
        date_QIND = time.strptime(date_string_QIND, '%Y%m%d')
        
        if date_res == date_QIND:
               for filename_randomError in filenames_randomError:
        
                   date_string_randomError = re.search('ERG.20[\d]{6}', filename_randomError).group()[4:]
                   date_randomError = time.strptime(date_string_randomError, '%Y%m%d')
        
                   if date_res == date_randomError: 
        
                       ds_randomError = gdal.Open(filename_randomError)
                       band_randomError = ds_randomError.GetRasterBand(1)
                       array_randomError = band_randomError.ReadAsArray()
                       
                       ds_QIND = gdal.Open(filename_QIND)
                       band_QIND = ds_QIND.GetRasterBand(1)
                       array_QIND = band_QIND.ReadAsArray()
            
                       for i in range(len(array_res)):
                           for j in range(len(array_res[i])):
                    
                               value_res = array_res[i][j]
                               value_QIND = array_QIND[i][j]
                               value_randomError = array_randomError[i][j]
                    
                               if value_res != -9999000 and value_QIND != -9999000 and value_randomError != -9999000:
                        
                                   if value_QIND < 0.3:
                                       low_randomError.append(value_randomError)
                                       low_res.append(abs(value_res))
                                     
                                   else:
                                       high_randomError.append(value_randomError)
                                       high_res.append(abs(value_res))                                    

##############################################################################
###                          LINEAR REGRESSION IMERG RANDOMERROR           ###
##############################################################################

# Create plot
fig = plt.figure()
ax = fig.add_subplot(111)

ax.scatter(high_randomError, high_res, alpha=0.8, c='blue', edgecolors='none', s=3, label='QIND > 0.3')
ax.scatter(low_randomError, low_res, alpha=0.8, c='red', edgecolors='none', s=3, label='QIND < 0.3')


plt.xlabel('randomError_IMERG')
plt.ylabel('Absolute residuals')

plt.legend(loc=2)
plt.show()

from sklearn.linear_model import LinearRegression

randomError = np.array(low_randomError + high_randomError).reshape((-1,1))
residuals = np.array(low_res + high_res)

model = LinearRegression().fit(randomError, residuals)

r_sq = model.score(randomError, residuals)

y_pred = model.predict(randomError)

# Calculate the point density
#xy = np.vstack([np.array(low_randomError + high_randomError),residuals])
#z = gaussian_kde(xy)(xy)

from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Create plot
fig = plt.figure()
ax = fig.add_subplot(111)
data = ax.hist2d(np.array(low_randomError + high_randomError), residuals, cmap = 'viridis',norm = LogNorm(), bins = 75)

#ax.scatter(randomError, residuals, alpha=0.8, c=z, edgecolors='none', s=3)
#ax.plot(randomError, y_pred)

plt.xlabel('randomError_IMERG')
plt.ylabel('Absolute residuals')
divider = make_axes_locatable(ax) #this and the following line are to make sure the colorbar is of same height as the image
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
cbar.minorticks_on()
cbar.ax.tick_params(labelsize=15)
plt.show()


#fig.subplots_adjust(wspace=0.18, hspace=0.13)
#plt.savefig(saveName, dpi=500,
#    bbox_inches='tight')
#plt.show()

##############################################################################
###                          OPERA RESIDUAL SCATTER PLOT                   ###
##############################################################################

OPERA_residual_path = '/home/bram/studie/thesis/data_analysis/residuals/1res_OPERA/2015'
OPERA_QIND_path = '/home/bram/studie/thesis/data_analysis/opera/3tiff_q_d/2015'

filenames_residuals = absoluteFilePaths(OPERA_residual_path)
filenames_QIND = absoluteFilePaths(OPERA_QIND_path)

QINDS = []
residuals = []

for filename_res in filenames_residuals:
    
    date_string_res = re.search('DWD_20[\d]{6}', filename_res).group()[4:]
    date_res = time.strptime(date_string_res, '%Y%m%d')
    
    ds_res = gdal.Open(filename_res)
    band_res = ds_res.GetRasterBand(1)
    array_res = band_res.ReadAsArray()
        
    for filename_QIND in filenames_QIND:
        
        date_string_QIND = re.search('ATE_20[\d]{6}', filename_QIND).group()[4:]
        date_QIND = time.strptime(date_string_QIND, '%Y%m%d')
        
        if date_res == date_QIND:
              
            ds_QIND = gdal.Open(filename_QIND)
            band_QIND = ds_QIND.GetRasterBand(1)
            array_QIND = band_QIND.ReadAsArray()
 
            for i in range(len(array_res)):
                for j in range(len(array_res[i])):
         
                    value_res = array_res[i][j]
                    value_QIND = array_QIND[i][j]
         
                    if value_res != -9999000 and value_QIND != -9999000:
             
                        QINDS.append(value_QIND)
                        residuals.append(abs(value_res))

from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Create plot
fig = plt.figure()
ax = fig.add_subplot(111)

data = ax.hist2d(QINDS, residuals, cmap = 'viridis', norm = LogNorm(), bins = 75, range = ([0, 1], [0, 100]))

#ax.scatter(randomError, residuals, alpha=0.8, c=z, edgecolors='none', s=3)
#ax.plot(randomError, y_pred)

plt.xlabel('OPERA Quality Index')
plt.ylabel('Absolute residuals')
divider = make_axes_locatable(ax) #this and the following line are to make sure the colorbar is of same height as the image
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
cbar.minorticks_on()
cbar.ax.tick_params(labelsize=15)
plt.show()

##############################################################################
###                          OPERA RESIDUAL SCATTER PLOT "ENHANCED"        ###
##############################################################################

DWD_path = '/home/bram/studie/thesis/data_analysis/dwd/7alignOPERA/2015'
OPERA_QIND_path = '/home/bram/studie/thesis/data_analysis/opera/3tiff_q_d/2015'
OPERA_path = '/home/bram/studie/thesis/data_analysis/opera/3tiff_p_d/2015'

filenames_OPERA = absoluteFilePaths(OPERA_path)
filenames_DWD = absoluteFilePaths(DWD_path)
filenames_QIND = absoluteFilePaths(OPERA_QIND_path)

QINDS = []
residuals = []

for filename_opera in filenames_OPERA:
    
    date_string_opera = re.search('ATE_20[\d]{6}', filename_opera).group()[4:]
    date_opera = time.strptime(date_string_opera, '%Y%m%d')
    
    ds_opera = gdal.Open(filename_opera)
    band_opera = ds_opera.GetRasterBand(1)
    array_opera = band_opera.ReadAsArray()
        
    for filename_DWD in filenames_DWD:
        
        date_string_DWD = re.search('002_20[\d]{6}', filename_DWD).group()[4:]
        date_DWD = time.strptime(date_string_DWD, '%Y%m%d')    
        
        if date_DWD == date_opera:
            
            ds_DWD = gdal.Open(filename_DWD)
            band_DWD = ds_DWD.GetRasterBand(1)
            array_DWD = band_DWD.ReadAsArray()       
 
            for filename_QIND in filenames_QIND:
                   
               date_string_QIND = re.search('ATE_20[\d]{6}', filename_QIND).group()[4:]
               date_QIND = time.strptime(date_string_QIND, '%Y%m%d')
                   
               if date_opera == date_QIND:
                         
                   ds_QIND = gdal.Open(filename_QIND)
                   band_QIND = ds_QIND.GetRasterBand(1)
                   array_QIND = band_QIND.ReadAsArray()   
                   
                   for i in range(len(array_opera)):
                       for j in range(len(array_opera[i])):
                        
                            value_dwd = array_DWD[i][j]
                            value_opera = array_opera[i][j]
                            value_QIND = array_QIND[i][j]
                     
                            if -9999000 not in [value_QIND, value_dwd, value_opera] and value_dwd >= 1:
                            
                                QINDS.append(value_QIND)
                                residuals.append(abs(value_opera - value_dwd))

from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Create plot
fig = plt.figure()
ax = fig.add_subplot(111)

data = ax.hist2d(QINDS, residuals, cmap = 'viridis',  bins = 75, range = ([0, 1], [0, 2]))

#ax.scatter(randomError, residuals, alpha=0.8, c=z, edgecolors='none', s=3)
#ax.plot(randomError, y_pred)

plt.xlabel('OPERA Quality Index')
plt.ylabel('Absolute residuals')
divider = make_axes_locatable(ax) #this and the following line are to make sure the colorbar is of same height as the image
cax = divider.append_axes("right", size="5%", pad=0.05)
cbar = plt.colorbar(data[3], cax = cax)#use data[3] because hist2d returns a tuple, the [3] selects the image 
cbar.minorticks_on()
cbar.ax.tick_params(labelsize=15)
plt.show()


count_1 = 0
count_non1 = 0
qinds_list = []

for filename_QIND in filenames_QIND:

              
    ds_QIND = gdal.Open(filename_QIND)
    band_QIND = ds_QIND.GetRasterBand(1)
    array_QIND = band_QIND.ReadAsArray()
    
    for row in array_QIND:
        for value in row:
            
            if value != -9999000:
                
                qinds_list.append(value)
fig = plt.figure()
# fixed bin size
bins = np.arange(0, 1, 0.01) # fixed bin size

plt.xlim([0, 1])

plt.hist(qinds_list, bins=bins, alpha=0.5)
plt.xlabel('Qind OPERA')
plt.ylabel('count')

plt.show()