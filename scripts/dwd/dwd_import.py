#!/usr/bin/env python3
"""
Script to convert 5-minute DWD .bin files to .asc

Created on Tue Oct 27 11:09:23 2020

"""
import wradlib as wrl 
import os
import re
import time

start_time = time.time()
os.system('export WRADLIB_DATA=/thesis/data_analysis/dwd')# export WRADLIB_DATA=/thesis/data_analysis/dwd

# return absoluteFilePaths as a list, similar generator yield function in importHDF5ODIM.py
def absoluteFilePaths(directory):
    result = []
    for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           result.append(os.path.join(dirpath, f))
    return result

# I did this per month, give
input_path = '/thesis/data_analysis/dwd/1Download_dwd/2017/YW2017.002_201712'
output_path = '/thesis/data_analysis/dwd/3aai/2017/12'

fn_bins = absoluteFilePaths(input_path)

for fn_bin in fn_bins:
    
    input_filename = os.path.join(input_path, fn_bin)
        
    data_raw, meta = wrl.io.read_radolan_composite(input_filename)
    
    # This is the RADOLAN projection
    proj_osr = wrl.georef.create_osr("dwd-radolan")
    
    # Get projected RADOLAN coordinates for corner definition
    xy_raw = wrl.georef.get_radolan_grid(1100, 900)
    data, xy = wrl.georef.set_raster_origin(data_raw, xy_raw, 'upper')
    
    proj_esri = proj_osr.Clone()
    proj_esri.MorphToESRI()
    ds = wrl.georef.create_raster_dataset(data, xy, projection=proj_esri)
    
    output_fn = fn_bin.split('/')[-1][:-10]+'.asc'
    
    folder_name = re.search('YW2017.002_20[\d]{6}', fn_bin).group()  
    output_folder_month = os.path.join(output_path, folder_name)
        
    if not os.path.exists(output_folder_month):
        os.makedirs(output_folder_month)
    
    output_file_path = os.path.join(output_folder_month, output_fn)
    wrl.io.write_raster_dataset(output_file_path, ds, 'AAIGrid', options=['DECIMAL_PRECISION=2'])
    
print("--- %s seconds ---" % (time.time() - start_time))