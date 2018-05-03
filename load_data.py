import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mpldates
from matplotlib.font_manager import FontProperties

import numpy as np
import random


cities = ["Halifax","London","Calgary"]
years = ['2013','2014']
#years = ['2014']


#cities = ["London","Calgary"]
calibrations = {'London': [('2013-01-01', '2013-06-14', 0.11764706),
                           ('2013-06-15', '2013-12-31', 0.12700911),
                           ('2014-01-01','2014-12-31', 0.132493585)],
                'Halifax': [('2013-01-01', '2013-05-14', 0.13616558),
                           ('2013-05-15', '2013-08-17', 0.13616558),
                           ('2013-08-18', '2013-12-31', 0.110765),
                           ('2014-01-01', '2014-12-31',0.1154284)],
                'Calgary':[('2013-01-01', '2013-05-16', 0.134947),
                           ('2013-05-17', '2013-10-18', 0.1112),
                           ('2014-01-01','2014-04-25',0.111247),
                           ('2014-04-26','2014-12-31',0.13888)]} 

#standardize data
stand = [['Humidity', 0,100],['Radiation', -100,600],['Wind', 0,5],['Rain', 0,20]
         ,['Temp', -15,35]]

def standardize(data):
    ans = data
    for n,low,high in stand:
        ans[n] = (data[n]-low)/(high-low)
    return ans


#ataList = []
def load_data(cities,years,path = "data/", resample = "6H",stand_data=True):
    DataList = []
    index = 0
    for (y,c) in  [(y,c)for y in years for c in cities ]:
        name = c + " Energy Balance 5min " + y
        print(name)
        Energy = pd.read_excel(path + name + '.xlsx',0,skiprows = [1,2,3],
                             usecols='C,O,Q,R,V',index_col=0,parse_dates=True,
                         dayfirst=True,header = 0,sep='\s*,\s*')


        name = c + " Water Balance 5min " + y
        print(name)

        Precipitation = pd.read_excel(path + name + '.xlsx',0,skiprows = [0,2,3],
                                          usecols='C,H',index_col=0,parse_dates=True,
                                          dayfirst=True,header = 0)
        for s,e,cf in calibrations[c]:
            Precipitation[s:e] *= cf

        name = c + " Lysimeters kg 5min" + y
        print(name)
        Lysimeter = pd.read_excel(path + name + '.xlsx',0,skiprows = [0,2,3,5],
                                          usecols='C,E,F',index_col=0,parse_dates=True,
                                          dayfirst=True,header = 0)
        Lysimeter = Lysimeter[(Lysimeter.T != 0).any()]
        Lysimeter = Lysimeter.mean(axis=1, skipna=True)


        result  = pd.concat([Energy, Precipitation,Lysimeter], axis=1).dropna(how='any')
        result = result.rename(index=str, columns={"fifteen" : "Radiation", "seventeen" : "Temp",
                                        "eighteen" : "Humidity", "twenty two" : "Wind",
                                        "["+c[0]+"] External raingauge" : "Rain",0 : "Lysimeter"})
        result = result.set_index(pd.DatetimeIndex(result.index))

        result = result.resample(resample,how={'Radiation': "mean",'Temp': "mean",'Humidity': "mean",
                                   'Wind': "mean",'Rain': "sum",'Lysimeter': "mean"})
        result = result.dropna(how='any')
        if(stand_data):
            result = standardize(result)
            
        DataList.append(result)
        
    
        index += 1
    return DataList
    print("Done Loading Data")
    



def gen_data(batch_size,num_steps,n_iterations,DataList,path = "data/", resample = "6H"):
    #if cities and years:
    #    print("Loading...")
    #load_data(cities,years,path=path,resample=resample)
        
    
    for iteration in range(n_iterations):
        data = random.choice(DataList)
        
        
        #index = num_steps
        
        
        x_data = data[['Radiation','Temp','Humidity','Wind','Rain']].as_matrix()
        y_data = data[['Lysimeter']].as_matrix()

        x_batch = np.zeros([batch_size,num_steps,5])
        y_batch = np.zeros([batch_size])
        
        for b in range(batch_size):
            index = random.randrange(num_steps,y_data.shape[0])
            x_batch[b] = x_data[index-num_steps:index]
            y_batch[b] = y_data[index-1]
            


        yield x_batch,y_batch
    