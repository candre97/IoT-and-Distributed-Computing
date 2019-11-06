#!/usr/bin/env python
# coding: utf-8

# In[1]:


from __future__ import print_function
from pyspark import SparkContext


# In[2]:



#combine training data
f1 = 'X_train.txt'
f2 =  'y_train.txt'


# In[3]:


combine =[]


# In[4]:


with open(f2) as xh:
  with open(f1) as yh:
    with open("train.txt","w") as zh:
      #Read first file
      xlines = xh.readlines()
      #Read second file
      ylines = yh.readlines()
      #Combine content of both lists
      #combine = list(zip(ylines,xlines))
      #Write to third file
      for i in range(len(xlines)):
        line = ylines[i].strip() + ' ' + xlines[i]
        zh.write(line)


# In[5]:



#close files
zh.close()
xh.close()
yh.close()


# In[6]:



#combine test data
e1 = 'X_test.txt'
e2 =  'y_test.txt'


# In[7]:



combine =[]

with open(e2) as xh:
  with open(e1) as yh:
    with open("test.txt","w") as zh:
#Read first file
xlines = xh.readlines()
#Read second file
ylines = yh.readlines()
#Combine content of both lists
#combine = list(zip(ylines,xlines))
#Write to third file
for i in range(len(xlines)):
  line = ylines[i].strip() + ' ' + xlines[i]
  zh.write(line)


# In[8]:



#close open files
zh.close()
xh.close()
yh.close()


# In[9]:


from pyspark.mllib.classification import SVMWithSGD, SVMModel
from pyspark.mllib.regression import LabeledPoint, LinearRegressionWithSGD, LinearRegressionModel


# In[10]:


sc = SparkContext(appName="lab10")


# In[11]:


# Load and parse the data
def parsePoint(line):
    values = [float(x) for x in line.split(' ')]
    return LabeledPoint(values[0], values[1:])


# In[12]:


data = sc.textFile("test.txt")
parsedData = data.map(parsePoint)


# In[13]:


model = LinearRegressionWithSGD.train(parsedData, iterations=100, step=0.00000001)


# In[14]:


from pyspark.mllib.evaluation import RegressionMetrics


# In[15]:


valuesAndPreds = parsedData.map(lambda p: (float(model.predict(p.features)), p.label))

# Instantiate metrics object
metrics = RegressionMetrics(valuesAndPreds)

# Squared Error
print("MSE = %s" % metrics.meanSquaredError)
print("RMSE = %s" % metrics.rootMeanSquaredError)

# R-squared
print("R-squared = %s" % metrics.r2)

# Mean absolute error
print("MAE = %s" % metrics.meanAbsoluteError)

# Explained variance
print("Explained variance = %s" % metrics.explainedVariance)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




