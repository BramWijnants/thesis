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
import re
import h5py

# gets ALL the absolute path filenames within the directory and subdirectories
def absolute_file_paths(directory):
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            if f.endswith('h5'):
                yield os.path.abspath(os.path.join(dirpath, f))

# path to input folder of files that will be warped (reprojected) and clipped
input_path = '/thesis/data_analysis/opera/1Downloaded_new/2017'
# path to output folder
output_path = '/thesis/data_analysis/opera/2tiff_p/2017'
# path to shapefile used for the clip
shp_path = '/thesis/map/Germany_Poly.shp'
# /dataset1 for precipitation rates / 15 minutes, dataset2 should be QIND
DatasetNr = "/dataset1"

# gets a list of ALL files within the input directories,
# generator object, use next(fn_bins) to go trough the filenames
fn_bins = absolute_file_paths(input_path)

# or loop trough the generated filenames from the fn_bins generator
for fn_bin in fn_bins:
    if os.path.getsize(fn_bin) > 0: # catch 'bad' files with 0 size
        if h5py.is_hdf5(fn_bin): # catch bad files that aren't hdf5

       # regex search for the month folder in the input filename
       # it searches for two digits with '/' on either sides
            month = re.search(r'/[\d]{2}/', fn_bin).group().strip('/')
       # create the output path as a string with the decided month folder
            output_folder_month = os.path.join(output_path, month)
       # create the full output filename
            output_fn = os.path.join(output_folder_month,
                                     os.path.split(fn_bin)[1].replace('h5','tif'))

       # make directory if it doesnt exist
            if not os.path.exists(output_folder_month):
                os.makedirs(output_folder_month)

        # if the ouput file doesnt exist the warp (reprojection and clip) will be executed
            if not os.path.exists(output_fn):
                os.system('gdalwarp -multi -t_srs EPSG:4326 -of GTiff '
                          '-srcnodata -9999000 -cutline {} -cl Germany_Poly '
                          '-crop_to_cutline HDF5:"{}":/{}/data1/data {}'
                          .format(shp_path, fn_bin, DatasetNr, output_fn))
