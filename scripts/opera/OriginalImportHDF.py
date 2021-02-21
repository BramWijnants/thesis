#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 00:04:45 2020

@author: bram
"""


def create_raster(output_path,
                  columns,
                  rows,
                  nband = 1,
                  gdal_data_type = gdal.GDT_Float64,
                  driver = r'GTiff'):
    ''' returns gdal data source raster object

    '''
    # create driver
    driver = gdal.GetDriverByName(driver)

    output_raster = driver.Create(output_path,
                                  int(columns),
                                  int(rows),
                                  nband,
                                  eType = gdal_data_type)    
    return output_raster

def numpy_array_to_raster(output_path,
                          numpy_array,
                          upper_left_tuple,
                          cell_resolution,
                          nband = 1,
                          no_data = 999,
                          gdal_data_type = gdal.GDT_Float64,
                          spatial_reference_system_wkid = 4326,
                          driver = r'GTiff'):
    ''' returns a gdal raster data source

    keyword arguments:

    output_path -- full path to the raster to be written to disk
    numpy_array -- numpy array containing data to write to raster
    upper_left_tuple -- the upper left point of the numpy array (should be a tuple structured as (x, y))
    cell_resolution -- the cell resolution of the output raster
    nband -- the band to write to in the output raster
    no_data -- value in numpy array that should be treated as no data
    gdal_data_type -- gdal data type of raster (see gdal documentation for list of values)
    spatial_reference_system_wkid -- well known id (wkid) of the spatial reference of the data
    driver -- string value of the gdal driver to use

    '''
    rows, columns = numpy_array.shape

    # create output raster
    output_raster = create_raster(output_path, int(columns), int(rows), nband, gdal_data_type)
    geotransform = (upper_left_tuple[0], cell_resolution, 0, upper_left_tuple[1], 0, -cell_resolution)
    spatial_reference = osr.SpatialReference()
    spatial_reference.ImportFromEPSG(spatial_reference_system_wkid)
    output_raster.SetProjection(spatial_reference.ExportToWkt())
    output_raster.SetGeoTransform(geotransform)
    output_band = output_raster.GetRasterBand(1)
    output_band.SetNoDataValue(no_data)
    output_band.WriteArray(numpy_array)          
    output_band.FlushCache()
    output_band.ComputeStatistics(False)

    return  output_raster

def read_OPRA(InputFileName, DatasetNr):