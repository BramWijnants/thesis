#!/usr/bin/env python3
"""
Script to warp the IMERG cleaned data into individual tiffs clipped to Germany

import gdal
options = gdal.WarpOptions(cutlineDSName=shp_path, srcSRS='EPSG:4326', format='GTiff', outputType=gdal.GDT_Float16)
gdal.Warp('test2.tif', 'NETCDF:"'+imerg_fn+'":precipitationUncal', outputType=gdal.GDT_Float64 , cutlineDSName=shp_path, format='GTiff', srcSRS='EPSG:4326', cropToCutline=True, cutlineLayer='Germany_poly')


Executed on 15 October 2020
"""
import os
import re
import time

# gets ALL the absolute path filenames within the directory and subdirectories
def absoluteFilePaths(directory): 
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           yield os.path.abspath(os.path.join(dirpath, f))

# Input IMERG folders, its gonna try ALL files in there so be careful
input_path = '/thesis/data_analysis/imerg/IMERG_cleaned/2015'

# Its gonna dump it here, make sure you have a similar folder structure setup
output_path = '/thesis/data_analysis/imerg/3clip/2015'

# path to shapefile used for the clip
shp_path = '/thesis/map/Germany_Poly.shp'

# datasets to be taken
datasets = ['precipitationCal', 'precipitationUncal', 'precipitationQualityIndex', 'randomError']

# gets a list of ALL files within the input directories,
# generator object, use next(fn_bins) to go trough the filenames
fn_bins = absoluteFilePaths(input_path) 

# loop trough the generated filenames from the fn_bins generator
for fn_bin in fn_bins: 
    
    date_string = re.search('IMERG.[\d]{8}', fn_bin).group().strip('IMERG.')
    date_time = time.strptime(date_string, '%Y%m%d')
    new_path = os.path.join(output_path,str(date_time.tm_mon).zfill(2), str(date_time.tm_mday).zfill(2))
    
    for dataset in datasets:
        # create the full output filename
        fn = fn_bin.split('/')[-1][:-26]+dataset+'.tif'
        output_fn = os.path.join(new_path, fn)
        
        # if the ouput file doesnt exist the warp (reprojection and clip) will be executed
        if not os.path.exists(output_fn):
            os.system('gdalwarp -s_srs EPSG:4326 -multi -of GTiff -dstnodata -9999000 -cutline {} -cl Germany_Poly -crop_to_cutline NETCDF:"{}":{} {}'.format(shp_path, fn_bin, dataset, output_fn))
    
