#!/usr/bin/env python3
"""
Script to "clean" IMERG data, not sure why it does what it does but it seems
to rotate the data 90 degrees to the correct coordinates, other than that, 
the units are converted from mm/h to mm

Executed on 15 Oktober using the save_multiple_imerg() function,
written the output to IMERG_cleaned folder
"""
import os
os.system('export HDF5_USE_FILE_LOCKING=FALSE')

def absoluteFilePaths(directory): 
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f[-3:] == 'tif':
               yield os.path.abspath(os.path.join(dirpath, f))

input_folder = '/thesis/data_analysis/imerg/4dail'

filenames = absoluteFilePaths(input_folder)

for old_filename in filenames:
    
    new_filename = (old_filename[:-4]+'.nc').replace('4dail', '5nc')
    
    os.system('gdal_translate -of netCDF -co "FORMAT=NC4" {} {}'.format(old_filename, new_filename))



