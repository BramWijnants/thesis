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
os.system('export WRADLIB_DATA=/home/bram/studie/thesis/data_analysis/dwd')# export WRADLIB_DATA=/home/bram/studie/thesis/data_analysis/dwd

# return absoluteFilePaths as a list, similar generator yield function in importHDF5ODIM.py
def absoluteFilePaths(directory):
    result = []
    for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           result.append(os.path.join(dirpath, f))
    return result

# I did this per month, give
input_path = '/media/bram/TOSHIBA EXT/thesis/Data_old/DWD/1Download_dwd/tars/2017/YW2017.002_201707/YW2017.002_20170708'
output_path = '/home/bram/studie/thesis/data_analysis/dwd/2aai/'

fn_bins = absoluteFilePaths(input_path)

for fn_bin in fn_bins:
    
    data_raw, meta = wrl.io.read_radolan_composite(fn_bin)
    
    # This is the RADOLAN projection
    proj_osr = wrl.georef.create_osr("dwd-radolan")
    
    # Get projected RADOLAN coordinates for corner definition
    xy_raw = wrl.georef.get_radolan_grid(1100, 900)
    data, xy = wrl.georef.set_raster_origin(data_raw, xy_raw, 'upper')
    
    masked_data = np.ma.masked_values(data, -9999)
    daily_nodata_count = np.sum(masked_data.mask)
    
    print(masked_data.data.max(), fn_bin)
    
    # Export to Arc/Info ASCII Grid format (aka ESRI grid)
    # only use first band
    proj_esri = proj_osr.Clone()
    proj_esri.MorphToESRI()
    ds = wrl.georef.create_raster_dataset(masked_data.data, xy, projection=proj_esri)
    
    #output_fn = fn_bin.split('/')[-1][:-10]+'.asc'
    
    #output_file_path = os.path.join(output_path, output_fn)
    #wrl.io.write_raster_dataset(output_file_path, ds, 'AAIGrid', options=['DECIMAL_PRECISION=2'])
    
    #print('day done')
    
    
