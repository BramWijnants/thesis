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
def save_multiple_imerg(imerg_path, save=True):

    warnings.filterwarnings("ignore", message="Converting a CFTimeIndex with dates from a non-standard calendar")
    imerg_filenames = get_filenames(imerg_path, '.HDF5.nc4')

    for imerg_filename in imerg_filenames:

        ds = import_single_imerg(imerg_filename)
        output_fn = imerg_filename.replace('IMERG_download', 'IMERG_cleaned')

        if not os.path.isfile(output_fn):
            ds.to_netcdf(output_fn)

# Import a single imerg file and return as xarray
def import_single_msg(imerg_filename, save=False):

    filesIMERG = xr.open_dataset(imerg_filename, decode_times=False)

    # Drop the variables which you are not going to use
    # Because precipitationCal and precipitationUncal are the same for the early and late run, I remove precipitationCal as well
    selectedVariables = filesIMERG.drop_vars(['azidiff', 'cth','cldmask','cph','ctt', 'dcld', 'dcot', 'dcwp', 'dndv', 'dreff', 'precip_ir', 'qa', 'reff', 'satz', 'sds', 'sds_cs', 'sds_diff', 'sds_diff_cs','sunz'])
    satelliteIMERG = selectedVariables.transpose()

    datetimeindex = satelliteIMERG.indexes['time'].to_datetimeindex()
    #satelliteIMERG['time'] = datetimeindex
    #satelliteIMERG['precipitationCal'] = satelliteIMERG['precipitationCal']/2 # Convert from mm/hr to mm
    #satelliteIMERG['precipitationUncal'] = satelliteIMERG['precipitationUncal']/2 # Convert from mm/hr to mm

    if save: # not used in a long time, probably not working correctly

        selectedVariables['precip'][0].to_netcdf('/home/bram/Desktop/TEST_MSG.nc4')

    return filesIMERG

if __name__ == '__main__':

    raw_msg_path = '/home/bram/studie/thesis/data_analysis/MSG/1Download/SEVIR_OPER_R___MSGCPP__L2__20180101T000000_20180102T000000_0001.nc'
    
    import_single_msg(raw_msg_path, True)
    
