#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 10:31:59 2020

@author: bram
"""
import gdal
import ogr


def write_shapefile(line, out_shp):
    """
    https://gis.stackexchange.com/a/52708/8104
    """
    # Now convert it to a shapefile with OGR    
    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource(out_shp)
    layer = ds.CreateLayer('', None, ogr.wkbMultiLineString)
    # Add one attribute
    layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    defn = layer.GetLayerDefn()

    ## If there are multiple geometries, put the "for" loop here

    # Create a new feature (attribute and geometry)
    feat = ogr.Feature(defn)
    feat.SetField('id', 123)

    # Make a geometry, from Shapely object
    geom = ogr.CreateGeometryFromWkb(line.ExportToWkb())
    feat.SetGeometry(geom)

    layer.CreateFeature(feat)
    feat = geom = None  # destroy these

    # Save and close everything
    ds = layer = feat = geom = None


"""
OPERA
"""

path = '/home/bram/studie/thesis/data_analysis/imerg/OPERA_Clip.tif'


ds_opera = gdal.Open(path, gdal.GA_ReadOnly)
band = ds_opera.GetRasterBand(1)
arr = band.ReadAsArray()

ul_x, pixel_width, rot, ul_y, rot, pixel_heigth = ds_opera.GetGeoTransform()
x_size = len(arr[0])
y_size = len(arr)



ur_x = ul_x + pixel_width * x_size
ur_y = ul_y

ll_x = ul_x
ll_y = ul_y + pixel_heigth * y_size

lr_x = ur_x
lr_y = ll_y

x1 = [ul_x + (x*pixel_width) for x in range(0, x_size+1)]
y1 = [ul_y for x in range(0, x_size+1)]

x2 = x1
y2 = [ll_y for x in range(0, x_size+1)]

x3 = [ll_x for x in range(0, y_size+1)]
y3 = [ul_y + (x*pixel_heigth) for x in range(0, y_size+1)]

x4 = [lr_x for x in range(0, y_size+1)]
y4 = y3

multiline = ogr.Geometry(ogr.wkbMultiLineString)

for i, x in enumerate(x1):
    y = y1[i]
    line1 = ogr.Geometry(ogr.wkbLineString)
    line1.AddPoint(x, y)
    line1.AddPoint(x2[i], y2[i])
    multiline.AddGeometry(line1)

for i, x in enumerate(x3):
    y = y3[i]
    line1 = ogr.Geometry(ogr.wkbLineString)
    line1.AddPoint(x, y)
    line1.AddPoint(x4[i], y4[i])
    multiline.AddGeometry(line1)

write_shapefile(multiline, 'OPERA_test.shp')


"""
IMERG
"""

path = '/home/bram/studie/thesis/data_analysis/imerg/WSG_Opera.tif'


ds_imerg = gdal.Open(path, gdal.GA_ReadOnly)
band = ds_imerg.GetRasterBand(1)
arr = band.ReadAsArray()

ul_x, pixel_width, rot, ul_y, rot, pixel_heigth = ds_imerg.GetGeoTransform()
x_size = len(arr[0])
y_size = len(arr)

ur_x = ul_x + pixel_width * x_size
ur_y = ul_y

ll_x = ul_x
ll_y = ul_y + pixel_heigth * y_size

lr_x = ur_x
lr_y = ll_y

x1 = [ul_x + (x*pixel_width) for x in range(0, x_size+1)]
y1 = [ul_y for x in range(0, x_size+1)]

x2 = x1
y2 = [ll_y for x in range(0, x_size+1)]

x3 = [ll_x for x in range(0, y_size+1)]
y3 = [ul_y + (x*pixel_heigth) for x in range(0, y_size+1)]

x4 = [lr_x for x in range(0, y_size+1)]
y4 = y3

multiline = ogr.Geometry(ogr.wkbMultiLineString)

for i, x in enumerate(x1):
    y = y1[i]
    line1 = ogr.Geometry(ogr.wkbLineString)
    line1.AddPoint(x, y)
    line1.AddPoint(x2[i], y2[i])
    multiline.AddGeometry(line1)

for i, x in enumerate(x3):
    y = y3[i]
    line1 = ogr.Geometry(ogr.wkbLineString)
    line1.AddPoint(x, y)
    line1.AddPoint(x4[i], y4[i])
    multiline.AddGeometry(line1)

write_shapefile(multiline, 'IMERG_test.shp')