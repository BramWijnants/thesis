#!/usr/bin/env python3
"""
Script to warp the hourly MSG .nc files into individual tiffs clipped to Germany

When using the gdal package rather than the os.system () call, something like:

import gdal    
ds = gdal.Warp('warp_test.tif', infile, dstSRS='EPSG:4326', outputType=gdal.GDT_Int16)


Executed on 26 November 2020
"""
import os

# gets ALL the absolute path filenames within the directory and subdirectories
def absoluteFilePaths(directory): 
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f.endswith('nc'):
               yield os.path.abspath(os.path.join(dirpath, f))

# I did this per month, give
input_path = '/home/bram/studie/thesis/data_analysis/MSG/1Download/2017'
output_path = '/home/bram/studie/thesis/data_analysis/MSG/1Download/2017'

# path to shapefile used for the clip
shp_path = '/home/bram/studie/thesis/map/Germany_Poly.shp'

# gets a list of ALL files within the input directories,
# generator object, use next(fn_bins) to go trough the filenames
fn_bins = absoluteFilePaths(input_path) 

# or loop trough the generated filenames from the fn_bins generator
for fn_bin in fn_bins: 
            
    # create the full output filename
    output_fn = (fn_bin[:-3].replace('1Download', '2clip'))+'_cth_warped.tif'
    
    # if the ouput file doesnt exist the warp (reprojection and clip) will be executed
    if not os.path.exists(output_fn):
        os.system('gdalwarp -s_srs EPSG:4326 -multi -srcnodata -999 -dstnodata -9999000 -cutline {} -cl Germany_Poly -crop_to_cutline NETCDF:"{}":cth {}'.format(shp_path, fn_bin,  output_fn))
