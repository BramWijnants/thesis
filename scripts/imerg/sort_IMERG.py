#!/usr/bin/env python3
"""
Created on Fri Oct 16 12:22:09 2020

"""
import os
import re
import time

# gets ALL the absolute path filenames within the directory and subdirectories
def absoluteFilePaths(directory): 
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           yield os.path.abspath(os.path.join(dirpath, f))

path = '/thesis/data_analysis/opera/2tiff_q/2015'

filenames = absoluteFilePaths(path)

for filename in filenames:
    
    if filename[-3:] == 'tif':
        date_string = re.search('_RATE_[\d]{8}', filename).group().strip('_RATE_')
        date_time = time.strptime(date_string, '%Y%m%d')
        new_path = os.path.join(path,str(date_time.tm_mon).zfill(2),str(date_time.tm_mday).zfill(2))
    
        if not os.path.exists(new_path):
            os.system('mkdir {}'.format(new_path))
        
 #       new_path = os.path.join(new_path, str(date_time.tm_hour).zfill(2))
        
 #       if not os.path.exists(new_path):
 #           os.system('mkdir {}'.format(new_path))
     
        os.system('mv {} {}'.format(filename, new_path))