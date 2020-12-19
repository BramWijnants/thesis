#!/usr/bin/env python3
"""
Script to make names better of IMERG 4dail
"""
import os

def absoluteFilePaths(directory): 
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f[-3:] == 'tif':
               yield os.path.abspath(os.path.join(dirpath, f))

input_folder = '/thesis/data_analysis/imerg/4dail/2017'

filenames = absoluteFilePaths(input_folder)

for filename in filenames:
    
    if 'randomError' in filename:
        
        fn = filename.split('/')[-1]
        output_fn = os.path.join(input_folder, 'randomError', fn)
        os.system('mv {} {}'.format(filename, output_fn))
    
    if 'precipitationCal' in filename:
        
        fn = filename.split('/')[-1]
        output_fn = os.path.join(input_folder, 'precipitationCal', fn)
        os.system('mv {} {}'.format(filename, output_fn))

    if 'precipitationUncal' in filename:
        
        fn = filename.split('/')[-1]
        output_fn = os.path.join(input_folder, 'precipitationUncal', fn)
        os.system('mv {} {}'.format(filename, output_fn))

    if 'precipitationQualityIndex' in filename:
        
        fn = filename.split('/')[-1]
        output_fn = os.path.join(input_folder, 'precipitationQualityIndex', fn)
        os.system('mv {} {}'.format(filename, output_fn))
