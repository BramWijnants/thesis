#!/usr/bin/env python3
"""
Script to "clean" IMERG data, not sure why it does what it does but it seems
to rotate the data 90 degrees to the correct coordinates, other than that,
the units are converted from mm/h to mm

Executed on 15 Oktober using the save_multiple_imerg() function,
written the output to IMERG_cleaned folder
"""
import re
import os
import warnings
import xarray as xr
os.system('export HDF5_USE_FILE_LOCKING=FALSE')

# Function to get the filenames within a directory with a given extension from
def get_filenames(path, extension):
    list_of_files = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith(extension):
                list_of_files.append(os.sep.join([dirpath, filename]))
    return list_of_files

# Create one xarray and net from all the imerge data in a given directory
def save_multiple_imerg(imerg_path, output_path, save=True):

    warnings.filterwarnings("ignore", message="Converting a CFTimeIndex with dates from a non-standard calendar")
    imerg_filenames = get_filenames(imerg_path, '.HDF5.nc')

    for imerg_filename in imerg_filenames:

        ds = import_single_imerg(imerg_filename)
        
        output_filename = imerg_filename.replace(raw_imerg_path, output_path)
        
        if not os.path.exists(output_path):
            os.system('mkdir {}'.format(output_path))
        
        ds.to_netcdf(output_filename)

# Import a single imerg file and return as xarray
def import_single_imerg(imerg_filename, save=False):
    
    filesIMERG = xr.open_dataset(imerg_filename)
    # Drop the variables which you are not going to use
    # Because precipitationCal and precipitationUncal are the same for the early and late run, I remove precipitationCal as well
    satelliteIMERG = filesIMERG.transpose('time', 'lat', 'lon')

    datetimeindex = satelliteIMERG.indexes['time'].to_datetimeindex()
    satelliteIMERG['time'] = datetimeindex
    satelliteIMERG['precipitationCal'] = satelliteIMERG['precipitationCal']/2 # Convert from mm/hr to mm

    return satelliteIMERG

if __name__ == '__main__':

    raw_imerg_path = '/home/bram/IMERG_cover/1231'
    output_path = '/home/bram/IMERG_cover/cleaned_1231'
    #raw_imerg_file = '/home/bram/studie/thesis/data_analysis/imerg/IMERG_download/2017/3B-HHR.MS.MRG.3IMERG.20170101-S013000-E015959.0090.V06B.HDF5.nc4'
    #imerg_ds = import_single_imerg(raw_imerg_file, True)
    save_multiple_imerg(raw_imerg_path, output_path)
