#!/usr/bin/env python3
"""
Script to make names better of IMERG 4dail
"""
import os

def absoluteFilePaths(directory): 
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           yield os.path.abspath(os.path.join(dirpath, f))

input_folder = '/home/bram/IMERG_cover'

filenames = absoluteFilePaths(input_folder)

for filename in filenames:
     
        output_fn = filename.split('?')[0]
        os.system('mv {} {}'.format(filename, output_fn))


