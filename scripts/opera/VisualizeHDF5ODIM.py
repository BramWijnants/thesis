# Python script
# Name: VisualizeHDF5ODIM.py
# Author: Aart Overeem (KNMI)
# Date: October 2019
# Description: Script to visualize ODIM HDF5 images over Europe.
#              Read ODIM HDF5 file, extract values, compute coordinates of polygons. Plot variable on a map using the polygons and associated values.
#              Output is a graphical file with a map.
# Usage: python3.7 VisualizeHDF5ODIM.py [input filename] [output graphical filename] [title of map] [legend text] [alpha value] [color scheme] [scale numbers] 
# [resolution of base map] [draw country borders] [ArcGis map?] [display color for values below lowest number] [draw coastlines] [font size of title] [colorbar] [extra text] 
# [DatasetNr in ODIM file]
# Example: python3.7 VisualizeHDF5ODIM.py RAD_OPERA_RAINFALL_RATE/2013/08/RAD_OPERA_RAINFALL_RATE_201308010015.h5 figures/RAD_OPERA_RAINFALL_RATE_201308010015.jpg 'OPERA radar rainfall map' 'Rainfall intensity (mm h$^{-1}$)' 1 
# 'YellowRed' '[0.1,0.5,1,2,3,4,5]' "h" "DrawCountries" "ArcGis" "DoNotColorSetUnder" "DrawCoastlines" 12 "ColorBar" "1 Aug 2013 0015 UTC" "/dataset1"

# Load Python packages:
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
from mpl_toolkits.basemap import Basemap, cm
import h5py
import pyproj
import pandas as pd

# Parameters from command line:    
InputFileName = 'RAD_OPERA_RAINFALL_RATE_201805291500.h5'
OutputFileName = 'opera_test.jpg'
TitlePlot = 'OPERA radar rainfall map'
LabelName = 'Rainfall intensity (mm h$^{-1}$)'
alpha = 1
ScaleType = 'YellowRed'	# 'Blues' or 'CbF' (= Colorblind Friendly)
levels = [0.1,0.5,1,2,3,4,5] # ticks of legend
LowestValue = min(levels)
ResolutionBaseMap = "h"	# Use "c" = crude for fast plotting.
DrawCountries = "DrawCountries"		# If DrawCountries is not equal to DrawCountries, the country borders are not drawn.
ArcGis = "ArcGis"			# If ArcGis is not equal to ArcGis, the background map from ArcGis is not plotted.
DoColorSetUnder = "DoNotColorSetUnder"
DrawCoastlines = "DrawCoastlines"
FontSizeTitle = 12
ColorBar = "ColorBar"
ExtraText = "1 Aug 2013 0015 UTC"
DatasetNr = "/dataset1"


##########################################################
# Read HDF5 files (ODIM HDF5 format) and obtain polygons.#
##########################################################

DATAFIELD_NAME = DatasetNr + '/data1/data'
FILE_NAME = InputFileName
f = h5py.File(FILE_NAME, mode='r')

# Read metadata:    
proj4str = f['/where'].attrs['projdef']
Ncols = np.int(f['/where'].attrs['xsize'])
Nrows = np.int(f['/where'].attrs['ysize'])

ATTR_NAME = DatasetNr + '/what'
zscale = f[ATTR_NAME].attrs['gain']
zoffset = f[ATTR_NAME].attrs['offset']
nodata = f[ATTR_NAME].attrs['nodata']
undetect = f[ATTR_NAME].attrs['undetect']

# Read data:
dset = f[DATAFIELD_NAME]
RArray = zoffset + zscale * dset[:]

# Read file with coordinates OPERA radar grid:
Grid = np.array(pd.read_csv("CoordinatesHDF5ODIM.dat", delimiter = " ", dtype="float",header=None))
Lon = Grid[:,0]
Lat = Grid[:,1]
p = pyproj.Proj('+proj=laea +lat_0=55.0 +lon_0=10.0 +x_0=1950000.0 +y_0=-2100000.0 +units=m +ellps=WGS84')
# resulting projection, WGS84, long, lat
outProj = pyproj.Proj(init='epsg:4326')
Xcoor, Ycoor = pyproj.transform(p,outProj,Lon,Lat)
#print(Xcoor,Ycoor)


# Convert image coordinates to longitude & latitude in degrees:
#p = pyproj.Proj(proj4str)
p = pyproj.Proj('+proj=laea +lat_0=55.0 +lon_0=10.0 +x_0=1950000.0 +y_0=-2100000.0 +units=m +ellps=WGS84')
LonArray = [[np.nan for x in range(Ncols)] for x in range(Nrows)]
LatArray = [[np.nan for x in range(Ncols)] for x in range(Nrows)]
# Obtain image coordinates of surrounding pixels (grid cells) needed to compute the coordinates of the polygons:
#Nrow = Nrows+1
#Ncol = Ncols+1
Nrow = Nrows
Ncol = Ncols
for j in range(0,Nrow):
   for i in range(0,Ncol):
      # Coordinate of pixel represents corner of pixel.
      LonArray[j][i] = Xcoor[i+j*Ncols]
      LatArray[j][i] = Ycoor[i+j*Ncols]
      #print(Xcoor[i+j*Ncols])
      #print(LonArray[j][i], LatArray[j][i])
      # The dimensions of X and Y should be one greater than those of C. 

#np.savetxt("test.dat",RArray , delimiter=",")

# No data values are made "not available".
RArray = np.array(RArray)
RArray = RArray.astype(float)
RArray[RArray == np.nan] = -1
RArray[np.isnan(RArray)] = -1
if DoColorSetUnder!="DoColorSetUnder":
   RArray[RArray < LowestValue] = np.nan
RArray[RArray == nodata] = np.nan
RArray[RArray == undetect] = np.nan
#https://stackoverflow.com/questions/34955158/what-might-be-the-cause-of-invalid-value-encountered-in-less-equal-in-numpy

# https://matplotlib.org/api/_as_gen/matplotlib.pyplot.pcolormesh.html:
# The dimensions of X and Y should be one greater than those of C. Alternatively, X, Y and C may have equal dimensions, in which case the last row and column of C will be ignored.
# Here the dimensions of X and Y are one greater than those of C. 

#RArray[765-1][700-1]=25 	#To test whether which value of R is used. -1 is used, since last row and column of R are automatically removed. 
#				This is indeed the last value on the map. See bottomcorner on the right in "RAD_NL25_RAC_MFBS_24H_201008270800_NL_WholeDomainTest.jpg".
# Also use #RArray[RArray == nodata] = 0 above instead of RArray[RArray == nodata] = np.nan. This makes the no data values white, so that the last RArray value stands out.
# Also change below the bounding box into llcrnrlon = 0.68, llcrnrlat = 48.4, urcrnrlon = 9.9, urcrnrlat = 56.03
# Also use dpi = 1600 in plt.savefig.



###############
# Make a plot.#
###############
type_of_service = "World_Shaded_Relief" 
plt.rcParams["font.family"] = "serif"
plt.rcParams.update({'font.size': 16}) 
plt.close('all')
m = Basemap(resolution = ResolutionBaseMap, llcrnrlon = -11, llcrnrlat = 32.5, urcrnrlon = 59.5, urcrnrlat = 67, epsg=3035, area_thresh=50.) #epsg:3035 = ETRS89 / ETRS-LAEA
#m = Basemap(resolution = ResolutionBaseMap, llcrnrlon = -180, llcrnrlat = -85, urcrnrlon = 180, urcrnrlat = 85, projection='cyl', area_thresh=100.)
# epsg code from RD New does not work with Basemap function.
# area_thresh=100: don't plot features smaller than 100 km^2, e.g. small lakes.

if ArcGis=="ArcGis":
   m.arcgisimage(service = type_of_service,dpi=100, xpixels = 10000, ypixels=None)
   # Retrieve an image using the ArcGIS Server REST API
   # xpixels 	requested number of image pixels in x-direction (default 400).
   # ypixels 	requested number of image pixels in y-direction. Default (None) is to infer the number from xpixels and the aspect ratio of the map projection region.
   # dpi 	The device resolution of the exported image (dots per inch, default 96).

if DrawCountries=="DrawCountries":
   m.drawcountries(linewidth=0.06) 

if DrawCoastlines=="DrawCoastlines":
   m.drawcoastlines(linewidth=0.06) 

# Draw parallels and meridians:
#parallels = np.arange(0.,91.,1.)
#m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10)
#meridians = np.arange(0.,30.,1.)
#m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10)

# Draw cross at position 5.2 E, 52 N:
#x1, y1 = m(5.2,52)
#plt.plot(x1, y1, '+', markersize=10, color='blue')

# Convert polygon coordinates to projection coordinates:
p1, p2 = m(np.asarray(LonArray),np.asarray(LatArray))
#print(p1,p2)
# Plot colored polygons:
# 4 classes for 'Blues' does not work well, then you get two white classes! In general, 4 classes seems not to work with get_cmap, so use at least 5 classes.
from matplotlib.colors import BoundaryNorm
# Lowest class, e.g. 1 - 26 mm includes the 1 values. Values below 1 are plotted in white. The highest value of the highest class is plotted in black or indigo.
# So for each class its lowest value, i.e. the lowest value at the tick mark, belongs to that class, whereas its highest value belongs to the next class.
# If CS3.cmap.set_over would not be used, values below 1 would also be plotted in the color of the lowest class! So use CS3.cmap.set_over. Alternatively, the code could be
# adapted so that all R values below 1 are set to nan.
if ScaleType=="Blues":
   levels = levels
   cmap = plt.get_cmap('Blues')
   colorSetOver = 'indigo'
   colorSetUnder = 'lightgray'
   
if ScaleType=="YellowRed":
   levels = levels
   cmap = mpl.colors.ListedColormap(['#ffffb2','#fed976','#feb24c','#fd8d3c','#f03b20','#bd0026'])
   colorSetOver = 'black'
   colorSetUnder = 'white'

if ScaleType=="CbF":
   levels = levels
   cmap = mpl.colors.ListedColormap(['#DBEED3','#9CD5C4','#71B5C7','#858AC1','#A2569C','#96344E'])
   colorSetOver = 'black'
   colorSetUnder = 'white'

norm = BoundaryNorm(levels, ncolors=cmap.N, clip=False)
if alpha<1:
   CS3 = plt.pcolormesh(p1,p2,RArray,alpha=alpha,cmap=cmap,norm=norm,edgecolor=(1,1,1,0),linewidth=0.001) # Grid lines now have (almost) same colour, but different from the colors
# of the filled polygons. File size is very large now: 21 MB.
# CS3 = plt.pcolormesh(p1,p2,RArray,alpha=alpha,cmap=cmap,norm=norm) # Grid lines have different colors, which do not match with the colors of the filled polygons. File size is 9 MB. 

if alpha==1:
   CS3 = plt.pcolormesh(p1,p2,RArray,alpha=alpha,cmap=cmap,norm=norm) 

CS3.cmap.set_over(colorSetOver)


if DoColorSetUnder=="DoColorSetUnder":
   CS3.cmap.set_under(colorSetUnder)
   if ColorBar=="ColorBar":
      # Plot color bar:
      cbar = plt.colorbar(pad=0.02,shrink=0.9,extend='both')
      cbar.set_label(LabelName)
else:
   if ColorBar=="ColorBar":
      # Plot color bar:
      cbar = plt.colorbar(pad=0.02,shrink=0.9,extend='max')
      cbar.set_label(LabelName)

# See for colour scales: https://matplotlib.org/examples/color/colormaps_reference.html

# Plot North arrow:
x1, y1 = m(29.5,33.5)
x2, y2 = m(29.5,37.5)
plt.annotate("", xy=(x2,y2), xytext=(x1,y1),arrowprops=dict(arrowstyle='simple',color="black"))
plt.text(x2, y2, 'N', fontsize=12)
# Standard 50 km scale bar. lon, lat, lon0, lat0, length
# Draw a map scale at lon,lat of length length representing distance in the map projection coordinates at lon0,lat0:
m.drawmapscale(-11.0, 70.3, 10, 52, 1000,barstyle='fancy',units='km',fontsize=7)
# Plot title:
#plt.title(TitlePlot)
plt.figtext(.5,.9,TitlePlot,fontsize=FontSizeTitle,ha='center')
x1, y1 = m(6,36)
plt.text(x1, y1, ExtraText, fontsize=11)
# Save figure:
plt.savefig(OutputFileName, bbox_inches = "tight", dpi = 800)

f.close()
