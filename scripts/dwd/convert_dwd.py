#!/usr/bin/env python3
"""
Script to make daily accumulations from 5-minute radklim (YW) precipitation accumulations

Executed for DWD data from 2015 on 15/10/2020

Author: Bram Wijnants
"""
import wradlib as wrl 
import os
import re
import numpy as np
os.system('export WRADLIB_DATA=/thesis/data_analysis/dwd')# export WRADLIB_DATA=/thesis/data_analysis/dwd

# return absoluteFilePaths as a list, similar generator yield function in importHDF5ODIM.py
def absoluteFilePaths(directory):
    result = []
    for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           result.append(os.path.join(dirpath, f))
    return result

# I did this per month, give
input_path = '/thesis/data_analysis/dwd/1Download_dwd/2017'
output_path = '/thesis/data_analysis/dwd/2aai'

daily_directories = os.listdir(input_path)

for day_directory in daily_directories:
    
    fn_bins = absoluteFilePaths(os.path.join(input_path, day_directory))
    
    if len(fn_bins) != 288:
        print(fn_bins[0])
        break
    
    data_raw, meta = wrl.io.read_radolan_composite(fn_bins[0])
    
    # This is the RADOLAN projection
    proj_osr = wrl.georef.create_osr("dwd-radolan")
    
    # Get projected RADOLAN coordinates for corner definition
    xy_raw = wrl.georef.get_radolan_grid(1100, 900)
    data, xy = wrl.georef.set_raster_origin(data_raw, xy_raw, 'upper')
    
    masked_data = np.ma.masked_values(data, -9999)
    
    for fn_bin in fn_bins[1:]:
        
        data_raw2, meta2 = wrl.io.read_radolan_composite(fn_bin)
        data2, xy2 = wrl.georef.set_raster_origin(data_raw, xy_raw, 'upper')
    
        masked_data2 = np.ma.masked_values(data2, -9999)
        
        if np.array_equal(masked_data.mask, masked_data2.mask):
            masked_data = masked_data + masked_data2
        
        else:
            print(fn_bin)
            break
    
    # Export to Arc/Info ASCII Grid format (aka ESRI grid)
    # only use first band
    proj_esri = proj_osr.Clone()
    proj_esri.MorphToESRI()
    ds = wrl.georef.create_raster_dataset(masked_data.data, xy, projection=proj_esri)
    
    folder_name = re.search('YW2017.002_20[\d]{6}', fn_bin).group()    
    output_folder_month = os.path.join(output_path, folder_name)
        
    if not os.path.exists(output_folder_month):
        os.makedirs(output_folder_month)
    
    output_fn = fn_bin.split('/')[-1][:-12]+'.asc'
    
    output_file_path = os.path.join(output_folder_month, output_fn)
    wrl.io.write_raster_dataset(output_file_path, ds, 'AAIGrid', options=['DECIMAL_PRECISION=2'])
    
    print('day done')
    
    
