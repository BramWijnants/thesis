#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to align a folder of grids to one reference grid

@author: bram
"""
import os
import gdal

def absoluteFilePaths(directory): 
   for dirpath, _, filenames in os.walk(directory):
       for filename in filenames:
           if filename.endswith('tif'):
               yield os.path.abspath(os.path.join(dirpath, filename))

input_folder = '/data/thesis/data_analysis/opera/3tiff_p_d/2015'
reference_grid = '/data/thesis/data_analysis/imerg/4dail/2015/precipitationCal/3B-HHR.MS.MRG.3IMERG.20150105-S123000-precipitationCal.tif'


ref_ds = gdal.Open(reference_grid)
Xmin, Xsize, junk,Ymax, junk, Ysize = ref_ds.GetGeoTransform()
array = ref_ds.GetRasterBand(1).ReadAsArray()
Yres, Xres = array.shape
Ymin = Ymax + (Yres * Ysize)
Xmax = Xmin + (Xres * Xsize)

filenames = absoluteFilePaths(input_folder)

for input_filename in filenames:
    
    output_filename = input_filename.replace('4dail','5aligned_opera')
    output_folder = os.path.dirname(output_filename)
    
    if not os.path.exists(output_folder):
        os.system('mkdir {}'.format(output_folder))
    
    # if the ouput file doesnt exist the warp (reprojection and clip) will be executed
    if not os.path.exists(output_filename):
         os.system('gdalwarp -multi -s_srs EPSG:4326 -t_srs EPSG:4326 -r "average" -srcnodata -9999000 -dstnodata -9999000                       -te {} {} {} {} -tr {} {} {} {}'.format(Xmin, Ymin, Xmax, Ymax, Xsize, Ysize, input_filename, output_filename))
