#!/usr/bin/env python3
"""
Script to make daily values from the IMERG 30-minute images

It sums the precipitation, converts to mm, and averages the QIND
The -8888000 (undetect) are set to 0
"""
import os
import gdal
import numpy as np

def absolute_file_paths(directory):
    result = []
    for dirpath, _, _filenames in os.walk(directory):
        for f in _filenames:
            if f.endswith('tif'):
                result.append(os.path.join(dirpath, f))
    return result

input_path = '/thesis/data_analysis/opera/2tiff_p/2017'
output_path = '/thesis/data_analysis/opera/3tiff_p_d/2017'

months = os.listdir(input_path)

for month_dir in months:

    month_path = os.path.join(input_path, month_dir)
    days = os.listdir(month_path)

    for day in days:

        days_path = os.path.join(month_path, day)

        filenames = absolute_file_paths(days_path)

        if len(filenames) == 96:
            first_file = gdal.Open(filenames[0])
            first_array = np.array(first_file.GetRasterBand(1).ReadAsArray())

            if '_q' in input_path:
                count = [np.zeros(len(x)) for x in first_array]
                count += first_array > 0

            else:
                first_array[first_array == -8888000] = 0

            for filename in filenames[1:]:

                if not os.path.exists(output_path+filename[63:]):

                    file = gdal.Open(filename)
                    array = np.array(file.GetRasterBand(1).ReadAsArray())

                    if '_q' not in input_path:
                        array[array == -8888000] = 0
                        for i, row in enumerate(array):
                            for j, value in enumerate(row):
                                if value >= 0 and first_array[i][j] >= 0:
                                    first_array[i][j] += value
                                elif first_array[i][j] < 0 <= value:
                                    first_array[i][j] == value

                    if '_q' in input_path:
                        for i, row in enumerate(array):
                            for j, value in enumerate(row):
                                if value > 0:
                                    count[i][j] += 1
                                    if first_array[i][j] < 0:
                                        first_array[i][j] = value
                                    else:
                                        first_array[i][j] += value

            if '_q' in input_path:
                for i, row in enumerate(count):
                    for j, value in enumerate(row):
                        if value != 0 and first_array[i][j] != -9999000:
                            first_array[i][j] /= value

            else:
                first_array[first_array != -9999000] *= 0.25

            driver = gdal.GetDriverByName('GTiff')
            dst_ds = driver.CreateCopy(output_path+filename[63:-6]+'.tif', first_file)

            dst_band = dst_ds.GetRasterBand(1)
            dst_band.WriteArray(first_array)
            dst_band.FlushCache()
            dst_band.ComputeStatistics(False)
