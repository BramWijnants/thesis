#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to make names better of DWD 3WSG
"""
import os

def absoluteFilePaths(directory): 
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f[-3:] == 'tif':
               yield os.path.abspath(os.path.join(dirpath, f))

input_folder = '/thesis/data_analysis/dwd/3wsg/2017'

filenames = absoluteFilePaths(input_folder)

for filename in filenames:
    
    new_filename = filename[:-6]+'.tif'
    os.system('mv {} {}'.format(filename, new_filename))

