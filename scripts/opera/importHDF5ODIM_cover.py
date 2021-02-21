#!/usr/bin/env python3
"""
Script to perform multiple gdalWarp operations as os.system() calls

gdalWarp allows to convert the original European 15 minute OPERA data
to WSG and clip to the extend of Germany, executed and finalized on 15/10/2020

When using the gdal package rather than the os.system () call, something like:

import gdal
ds = gdal.Warp('warp_test.tif', infile, dstSRS='EPSG:4326', outputType=gdal.GDT_Int16)

Author: Bram Wijnants
"""
import os

# gets ALL the absolute path filenames within the directory and subdirectories
def absolute_file_paths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            yield os.path.abspath(os.path.join(dirpath, f))



folder= '1231'
input_path = os.path.join('/home/bram/github/thesis/cover_data',folder)
output_path = os.path.join('/home/bram/github/thesis/cover_data', folder+'_tiff')
DatasetNr = "/dataset1"

fn_bins = absolute_file_paths(input_path)

for fn_bin in fn_bins:

    output_fn = os.path.join(output_path, os.path.split(fn_bin)[1].split('.')[0]+'.tif')
    
    # make directory if it doesnt exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    
     # if the ouput file doesnt exist the warp (reprojection and clip) will be executed
    if not os.path.exists(output_fn):
        os.system('gdalwarp -multi -t_srs EPSG:4326 -of GTiff '
                   '-srcnodata -9999000 HDF5:"{}":/{}/data1/data {}'
                   .format(fn_bin, DatasetNr, output_fn))
