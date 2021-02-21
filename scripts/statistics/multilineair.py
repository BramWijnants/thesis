import os
import re
import numpy as np
import pandas as pd
import gdal
import matplotlib.pyplot as plt
from sklearn import linear_model
import statsmodels.api as sm

def find_matching_days(path1, path2, path3):
    result = {}
    
    file_paths1 = absoluteFilePaths(path1)
    file_paths2 = absoluteFilePaths(path2)
    file_paths3 = absoluteFilePaths(path3)

    for filename1 in file_paths1:
        date_string = re.search(r'20[\d]{6}', filename1).group()
        for filename2 in file_paths2:
            if date_string in filename2:
                for filename3 in file_paths3:
                    if date_string in filename3:
                        result[date_string] = [filename1, filename2, filename3]
    return result

def absoluteFilePaths(directory): 
    results = []
    for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f.endswith('tif'):
               results.append(os.path.abspath(os.path.join(dirpath, f)))
    return results

def getArray(filename, nodata=False):
    ds = gdal.Open(filename)
    band = ds.GetRasterBand(1)
    array = band.ReadAsArray()
    if nodata:
        masked_array = np.ma.masked_values(array, nodata)
        return masked_array
    else:
        return array

def plot_scatter(y, x, labelY, labelX):
    
    plt.scatter(y, x, color='red')
    plt.title(labelX+' Vs '+labelY, fontsize=14)
    plt.xlabel(labelX, fontsize=14)
    plt.ylabel(labelY, fontsize=14)
    plt.grid(True)
    plt.show()
    
    


if __name__ == '__main__':
    
    residual_path = '/data/thesis/data_analysis/residuals/2res_OPERA_masked/2015'
    dem_path = '/data/thesis/data_analysis/dem/srtm_germany_dsm_aligned_opera.tif'
    qind_path = '/data/thesis/data_analysis/opera/3tiff_q_d/2015'
    qind_path = '/data/thesis/data_analysis/imerg/5aligned_opera/2015/randomError'
    cth_path = '/data/thesis/data_analysis/opera/3tiff_q_d/2015'

    filenames = find_matching_days(residual_path, qind_path, cth_path)
    
    data= {'Residual':[],'Qind':[],'CTH':[],'Elevation':[]}

    dem_array = getArray(dem_path)

    for date, (res_fn, qind_fn, cth_fn) in filenames.items():
        
        res_array = getArray(res_fn)
        qind_array = getArray(qind_fn)
        cth_array = getArray(cth_fn)

        for i in range(len(res_array)):
            for j in range(len(res_array[i])-1):
                
                res = res_array[i][j]
                qind = qind_array[i][j]
                cth = cth_array[i][j]
                dem = dem_array[i][j]
                
                if -9999000 not in [res, qind, cth, dem]:
                    
                    data['Residual'].append(abs(res))
                    data['Qind'].append(qind)
                    data['CTH'].append(cth)
                    data['Elevation'].append(dem)
                
    df = pd.DataFrame(data,columns=['Residual','Qind','CTH']) 
    
    X = df[['Qind','CTH']] # here we have 2 variables for multiple regression. If you just want to use one variable for simple linear regression, then use X = df['Interest_Rate'] for example.Alternatively, you may add additional variables within the brackets
    Y = df['Residual']
     
    # with sklearn
    regr = linear_model.LinearRegression()
    regr.fit(X, Y)
    
    print('Intercept: \n', regr.intercept_)
    print('Coefficients: \n', regr.coef_)
    
    # with statsmodels
    X = sm.add_constant(X) # adding a constant
     
    model = sm.OLS(Y, X).fit()
    predictions = model.predict(X) 
     
    print_model = model.summary()
    print(print_model)

    dem_path = '/data/thesis/data_analysis/dem/srtm_germany_dsm_aligned_imerg.tif'
    bias_path = '/data/thesis/data_analysis/relative_bias/output/relative_bias_IMERG.tif'

    data= {'Bias':[],'Elevation':[]}

    dem_array = getArray(dem_path)
    bias_array = getArray(bias_path)



    for i in range(len(dem_array)):
        for j in range(len(dem_array[i])):
            
            bias = bias_array[i][j]
            dem = dem_array[i][j]
            
            if -9999000 not in [bias, dem]:
                
                data['Bias'].append(bias)
                data['Elevation'].append(dem)
            
    df = pd.DataFrame(data,columns=['Bias','Elevation']) 
    
    X = df['Elevation'] # here we have 2 variables for multiple regression. If you just want to use one variable for simple linear regression, then use X = df['Interest_Rate'] for example.Alternatively, you may add additional variables within the brackets
    Y = df['Bias']
     
    # with sklearn
    regr = linear_model.LinearRegression()
    regr.fit(X, Y)
    
    print('Intercept: \n', regr.intercept_)
    print('Coefficients: \n', regr.coef_)
    
    # prediction with sklearn
    New_Interest_Rate = 2.75
    New_Unemployment_Rate = 5.3
    print ('Predicted Stock Index Price: \n', regr.predict([[New_Interest_Rate ,New_Unemployment_Rate]]))
    
    # with statsmodels
    X = sm.add_constant(X) # adding a constant
     
    model = sm.OLS(Y, X).fit()
    predictions = model.predict(X) 
     
    print_model = model.summary()
    print(print_model)
    
    def find_matching_days(path1, path2):
        result = {}
        
        file_paths1 = absoluteFilePaths(path1)
        file_paths2 = absoluteFilePaths(path2)
    
        for filename1 in file_paths1:
            date_string = re.search(r'20[\d]{6}', filename1).group()
            for filename2 in file_paths2:
                if date_string in filename2:
                    result[date_string] = [filename1, filename2]
        return result
        
    p_path = '/data/thesis/data_analysis/opera/3tiff_p_d/2015'
    cth_path = '/data/thesis/data_analysis/MSG/3align_opera/2015/cth'

    filenames = find_matching_days(p_path, cth_path)
    
    data= {'P':[],'CTH':[]}

    for date, (P_fn, cth_fn) in filenames.items():
        
        P_array = getArray(P_fn)
        cth_array = getArray(cth_fn)

        for i in range(len(P_array)):
            for j in range(len(P_array[i])):
                
                P = P_array[i][j]
                cth = cth_array[i][j]
                
                if -9999000 not in [P, cth]:
                    
                    data['P'].append(P)
                    data['CTH'].append(cth)
            
    df = pd.DataFrame(data,columns=['P','CTH']) 
    
    X = df['CTH'] # here we have 2 variables for multiple regression. If you just want to use one variable for simple linear regression, then use X = df['Interest_Rate'] for example.Alternatively, you may add additional variables within the brackets
    Y = df['P']
     
    # with sklearn
    regr = linear_model.LinearRegression()
    regr.fit(X, Y)
    
    print('Intercept: \n', regr.intercept_)
    print('Coefficients: \n', regr.coef_)
    
    # with statsmodels
    X = sm.add_constant(X) # adding a constant
     
    model = sm.OLS(Y, X).fit()
    predictions = model.predict(X) 
     
    print_model = model.summary()
    print(print_model)
    
    