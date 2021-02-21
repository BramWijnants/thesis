#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 14:33:00 2020

@author: bram
"""
#!/usr/bin/env python3
"""
Script to "clean" IMERG data, not sure why it does what it does but it seems
to rotate the data 90 degrees to the correct coordinates, other than that, 
the units are converted from mm/h to mm

Executed on 15 Oktober using the save_multiple_imerg() function,
written the output to IMERG_cleaned folder
"""
import re
import os
import datetime
import xarray as xr
import numpy as np
os.system('export HDF5_USE_FILE_LOCKING=FALSE')

# Function to get the filenames within a directory with a given extension from
def get_filenames(path, extension):
    list_of_files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith(extension): 
                list_of_files.append(os.sep.join([dirpath, filename]))
    return list_of_files

# Create one xarray and net from all the imerge data in a given directory
def save_multiple_imerg(imerg_path):
    
    imerg_filenames = get_filenames(imerg_path, '.nc')
    first_ds = xr.open_dataset(imerg_filenames[0], drop_variables='time', decode_times=False)
    
    date_string = re.search('IMERG.[\d]{8}', imerg_filenames[0]).group().strip('IMERG.')
    date_time = datetime.datetime.strptime(date_string, '%Y%m%d')
    first_ds['time'] = np.array([date_time])
    
    for i, imerg_filename in enumerate(imerg_filenames[1:]):
        
        ds = xr.open_dataset(imerg_filename, drop_variables='time')
        date_string = re.search('IMERG.[\d]{8}', imerg_filename).group().strip('IMERG.')
        date_time = datetime.datetime.strptime(date_string, '%Y%m%d')
        ds['time'] = np.array([date_time])

        first_ds = xr.concat([first_ds, ds], 'time')
    
    first_ds.to_netcdf('/home/bram/studie/thesis/data_analysis/imerg/5nc/2015/IMERG_2015_precipitationCal.nc')

if __name__ == '__main__':

    raw_imerg_path = '/home/bram/studie/thesis/data_analysis/imerg/5nc/2015/precipitationCal'
    #raw_imerg_file = '/home/bram/studie/thesis/data_analysis/imerg/IMERG_download/2017/3B-HHR.MS.MRG.3IMERG.20170101-S013000-E015959.0090.V06B.HDF5.nc4'
    #imerg_ds = import_single_imerg(raw_imerg_file, True)
    imerg_ds = save_multiple_imerg(raw_imerg_path)
    
    

