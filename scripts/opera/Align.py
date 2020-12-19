#!/usr/bin/env python3
"""
Created on Tue Oct 20 10:23:31 2020

"""
import os
import gdal

def absoluteFilePaths(directory): 
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f.endswith('tif'):
               yield os.path.abspath(os.path.join(dirpath, f))

input_folder = '/thesis/data_analysis/imerg/4dail/2015/precipitationCal'
reference_grid = '/thesis/data_analysis/opera/3tiff_p_d/2015/RAD_OPERA_RAINFALL_RATE_2015010109.tif'
#reference_grid = '/thesis/data_analysis/imerg/4dail/2015/precipitationCal/B-HHR.MS.MRG.3IMERG.20150114-S030000-precipitationCal.tif'

ref_ds = gdal.Open(reference_grid)
Xmin, Xsize, junk,Ymax, junk, Ysize = ref_ds.GetGeoTransform()
array = ref_ds.GetRasterBand(1).ReadAsArray()
Yres, Xres = array.shape
Ymin = Ymax + (Yres * Ysize)
Xmax = Xmin + (Xres * Xsize)

filenames = absoluteFilePaths(input_folder)

for input_filename in filenames:
    
    #output_filename = input_filename.replace('3wsg','4alignIMERG')[:-8]+'.tif'
    output_filename = input_filename.replace('4dail','5aligned_opera')
    # if the ouput file doesnt exist the warp (reprojection and clip) will be executed
    #print('gdalwarp -multi -wo NUM_THREADS=8 -te {} {} {} {} -tr {} {} -tap {} {}'.format(Xmin, Ymin, Xmax, Ymax, Xres, Yres, input_filename, output_filename))
    os.system('gdalwarp -multi -s_srs EPSG:4326 -t_srs EPSG:4326 -r "average" -srcnodata -9999000 -dstnodata -9999000 -te {} {} {} {} -tr {} {} {} {}'.format(Xmin, Ymin, Xmax, Ymax, Xsize, Ysize, input_filename, output_filename))
    #os.system('gdalwarp -multi -s_srs EPSG:4326  -srcnodata -9999000 -dstnodata -9999000  -te {} {} {} {} -tr {} {} -tap {} {}'.format(Xmin, Ymin, Xmax, Ymax, Xres, Yres, input_filename, output_filename))
