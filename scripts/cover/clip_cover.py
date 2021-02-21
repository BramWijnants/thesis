#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  2 13:44:29 2021

@author: bram
"""
import os
import re
import gdal
import shapefile
from shapely.geometry import Point # Point class
from shapely.geometry import shape # shape() is a function to convert geo objects through the interface

def absoluteFilePaths(directory, start): 
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if not f.startswith(start):
               yield os.path.abspath(os.path.join(dirpath, f))


def index_to_wsg(x,y,geo):
    xoffset, px_w, rot1, yoffset, rot2, px_h = geo

    # supposing x and y are your pixel coordinate this 
    # is how to get the coordinate in space.
    posX = px_w * x + rot1 * y + xoffset
    posY = rot2 * x + px_h * y + yoffset
    
    # shift to the center of the pixel
    posX += px_w / 2.0
    posY += px_h / 2.0
    
    return posX, posY


def wsg_to_index(x, y, geo):
    
    TL_x, x_res, _, TL_y, _, y_res = geo
    x_index = (x - TL_x) / x_res
    y_index = (y - TL_y) / y_res
    
    return round(y_index), round(x_index)


def write_raster(output_filename, copy_filename, array):
    
    ds = gdal.Open(copy_filename)
    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.CreateCopy(output_filename, ds)
    dst_band = dst_ds.GetRasterBand(1)
    dst_band.WriteArray(array)
    dst_band.ComputeStatistics(True)
    ds.FlushCache()
    dst_ds.FlushCache()


if __name__ == '__main__':
    
    shapefile_path = '/media/bram/Data/thesis/map/Germany_Poly.shp'
    data_path = '/home/bram/github/thesis/cover_data/cleaned'
    output_path = '/home/bram/github/thesis/cover_data/output'   
    
    shp = shapefile.Reader(shapefile_path) #open the shapefile
    all_shapes = shp.shapes() # get all the polygons
    boundary = all_shapes[0] # get a boundary polygon
    
    filenames_gen = absoluteFilePaths(data_path, 'YW')
    
    for filename in filenames_gen:
        
        ds = gdal.Open(filename)
        array = ds.GetRasterBand(1).ReadAsArray()
        geo = ds.GetGeoTransform()
        
        date = re.search('2015[\d]{4}', filename).group()
        
        filenames_dwd = absoluteFilePaths(data_path, ('RAD', '3B'))
        filename_dwd = [x for x in filenames_dwd if date in x][0]
        
        ds_dwd = gdal.Open(filename_dwd)
        array_dwd = ds_dwd.GetRasterBand(1).ReadAsArray()
        geo_dwd = ds_dwd.GetGeoTransform()
        
        for i in range(len(array)):
            for j in range(len(array[i])):
                
                value = array[i][j]
                posX, posY = index_to_wsg(j,i, geo)
                in_shape = Point((posX, posY)).within(shape(boundary))
                indexX_dwd, indexY_dwd = wsg_to_index(posX, posY, geo_dwd)
                
                if (indexX_dwd >= 0 and indexY_dwd >= 0 and indexX_dwd < len(array_dwd) and indexY_dwd < len(array_dwd[0])) or in_shape:
                    value_dwd = array_dwd[indexX_dwd][indexY_dwd]
                    
                    if value_dwd != -9999000. or in_shape:
                        continue
                    
                    else:
                        array[i][j] = -9999000
                
                else: 
                    array[i][j] = -9999000
                
        output_filename = os.path.join(output_path, os.path.split(filename)[1][:-4]+'_clipped.tif')
        write_raster(output_filename, filename, array)
