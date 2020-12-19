#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import h5py
from pyproj import CRS, Transformer
import xarray as xr

path = '/thesis/data_analysis/KNMI/dataset-download/RADNL_CLIM____MFBSNL25_24H_20171231T010000_20190101T000000_0002/RAD_NL25_RAC_MFBS_24H/2018/05/RAD_NL25_RAC_MFBS_24H_201805291500_NL.h5'

f = h5py.File(path, 'r')

data = f['image1']['image_data'][()]

hello = xr.DataArray(data)

hello['dim_0']=list(range(0,10,1))








with h5py.File(path, 'r') as f:
   proj4 = str(list(f['geographic/map_projection'].attrs.items())[2][1])
   proj4 = proj4[2:len(proj4)-1]
   proj4 = '+proj=stere +lat_0=90 +lon_0=0.0 +lat_ts=60.0 +a=6378137 +b=6356752 +x_0=0 +y_0=0'
   from_proj = CRS.from_proj4(proj4)
   to_proj = CRS.from_proj4("+proj=longlat +datum=WGS84 +no_defs +ellps=WGS84 +towgs84=0,0,0")
   print(from_proj)
   print(to_proj)
   transform = Transformer.from_crs(from_proj, to_proj)
   