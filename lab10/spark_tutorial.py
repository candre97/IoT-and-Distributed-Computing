#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pyspark
from pyspark import SparkContext
sc =SparkContext()


# In[2]:


# create a collection of data (RDD)
nums = sc.parallelize([1,2,3,4])


# In[3]:


# access the first row
nums.take(1)


# In[4]:


# You can apply a transformation to the data with a lambda function. 
# In the example below, you return the square of nums. 
# It is a map transformation

squared = nums.map(lambda x: x*x).collect()
for num in squared:
    print('%i ' % (num))


# In[5]:


# Spark Context
from pyspark.sql import Row
from pyspark.sql import SQLContext

sqlContext = SQLContext(sc)


# In[6]:


# create a list of tuple
ppl = [('John',19),('Smith',29),('Adam',35),('Henry',50)]


# In[7]:


rdd = sc.parallelize(ppl)


# In[8]:


# convert the tuples
rdd.map(lambda x: Row(name=x[0], age=int(x[1])))			


# In[9]:


# create a dataFrame context
sqlContext.createDataFrame(ppl)
list_p = [('John',19),('Smith',29),('Adam',35),('Henry',50)]
rdd = sc.parallelize(list_p)
ppl = rdd.map(lambda x: Row(name=x[0], age=int(x[1])))
DF_ppl = sqlContext.createDataFrame(ppl)


# In[10]:


# access the type of each feature
DF_ppl.printSchema()


# In[11]:


# Machine Learning with Spark
# 1) Basic operation with PySpark

#initialize the SCLContext
#from pyspark.sql import SQLContext
url = "https://raw.githubusercontent.com/guru99-edu/R-Programming/master/adult_data.csv"
from pyspark import SparkFiles
sc.addFile(url)
sqlContext = SQLContext(sc)


# In[12]:


#read the CSV file with sqlContext.read.csv
df = sqlContext.read.csv(SparkFiles.get("adult_data.csv"), header=True, inferSchema= True)	


# In[13]:


df.printSchema()


# In[14]:


df.show(5, truncate = False)


# In[15]:


df_string = sqlContext.read.csv(SparkFiles.get("adult_data.csv"), header=True, inferSchema=  False)
df_string.printSchema()


# In[16]:


# note in tutorial on withColumn & inderShema
# Import all from `sql.types`
from pyspark.sql.types import *


# In[17]:


# Write a custom function to convert the data type of DataFrame columns
def convertColumn(df, names, newType):
    for name in names: 
        df = df.withColumn(name, df[name].cast(newType))
    return df 


# In[18]:


# List of continuous features
CONTI_FEATURES  = ['age', 'fnlwgt','capital-gain', 'educational-num', 'capital-loss', 'hours-per-week']
# Convert the type
df_string = convertColumn(df_string, CONTI_FEATURES, FloatType())
# Check the dataset
df_string.printSchema()


# In[19]:


# select columns
df.select('age', 'fnlwgt').show(5)


# In[20]:


# If you want to count the number of occurence by group, you can chain:
# groupBy()
# count()

# you count the number of rows by the education level.
df.groupBy("education").count().sort("count",ascending=True).show()			


# In[21]:


# Describe the Data
df.describe().show()


# In[22]:


# summary stats of only one column
df.describe('age').show()


# In[23]:


# crosstab computation
df.crosstab('age', 'income').sort("age_income").show()


# In[24]:


# drop column
df.drop('education_num').columns


# In[25]:


# filter data
df.filter(df.age > 40).count()


# In[26]:


# group data and compute statistical operations
df.groupby('marital-status').agg({'capital-gain': 'mean'}).show()			


# In[27]:


# data preprocessing -- square the age. 
from pyspark.sql.functions import *


# In[28]:


# 1 Select the column
age_square = df.select(col("age")**2)


# In[29]:


# 2 Apply the transformation and add it to the DataFrame
df = df.withColumn("age_square", col("age")**2)


# In[30]:


df.printSchema()


# In[31]:


# reorder the columns

COLUMNS = ['age', 'age_square', 'workclass', 'fnlwgt', 'education', 'educational-num', 'marital-status',
           'occupation', 'relationship', 'race', 'gender', 'capital-gain', 'capital-loss',
           'hours-per-week', 'native-country', 'income']
df = df.select(COLUMNS)
df.first()


# In[32]:


# exclude some data (filter out bad data)
df.groupby('native-country').agg({'native-country': 'count'}).sort(asc("count(native-country)")).show()


# In[33]:


#df_remove = df.filter(df.native-country != 'Holand-Netherlands')


# In[34]:


from pyspark.ml.feature import StringIndexer, OneHotEncoder


# In[35]:


# build data processing pipeline

# select the string column to index.

si = StringIndexer(inputCol="workclass", outputCol="workclass_encoded")		


# In[36]:


# fit data, transform it
model = si.fit(df)
indexed = model.transform(df)


# In[37]:


# create news columns based on the group
OneHotEncoder(dropLast=False, inputCol="workclassencoded", outputCol="workclassvec")


# In[38]:


### Example encoder
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler


# In[39]:


stringIndexer = StringIndexer(inputCol="workclass", outputCol="workclass_encoded")
model = stringIndexer.fit(df)
indexed = model.transform(df)
encoder = OneHotEncoder(dropLast=False, inputCol="workclass_encoded", outputCol="workclass_vec")
encoded = encoder.transform(indexed)
encoded.show(2)


# In[40]:


# build the pipeline

from pyspark.ml import Pipeline
from pyspark.ml.feature import OneHotEncoderEstimator


# In[41]:


CATE_FEATURES = ['workclass', 'education', 'marital-status', 'occupation', 'relationship', 'race', 'gender', 'native-country']
stages = [] # stages in our Pipeline


# In[42]:


# encode the categorical data
for categoricalCol in CATE_FEATURES:
    stringIndexer = StringIndexer(inputCol=categoricalCol, outputCol=categoricalCol + "Index")
    encoder = OneHotEncoderEstimator(inputCols=[stringIndexer.getOutputCol()],
                                     outputCols=[categoricalCol + "classVec"])
    stages += [stringIndexer, encoder]


# In[43]:


# index the label feature
label_stringIdx =  StringIndexer(inputCol="gender", outputCol="newlabel")
stages += [label_stringIdx]


# In[44]:


# add continuous variable
assemblerInputs = [c + "classVec" for c in CATE_FEATURES] + CONTI_FEATURES


# In[45]:


# assemble the steps
assembler = VectorAssembler(inputCols=assemblerInputs, outputCol="features")
stages += [assembler]


# In[46]:


# push the data to the pipeline
# Create a Pipeline.
pipeline = Pipeline(stages=stages)
pipelineModel = pipeline.fit(df)
model = pipelineModel.transform(df)


# In[47]:


model.take(1)


# In[48]:


# build the classifier

#convert data to a dataFrame
from pyspark.ml.linalg import DenseVector
input_data = model.rdd.map(lambda x: (x["newlabel"], DenseVector(x["features"])))


# In[49]:


# create the training data as a data frame
df_train = sqlContext.createDataFrame(input_data, ["label", "features"])			


# In[50]:


# check row 2
df_train.show(2)


# In[51]:


# You split the dataset 80/20 with randomSplit.
train_data, test_data = df_train.randomSplit([.8,.2],seed=1234)


# In[52]:


# how many people with income below/above 50k in both training and test set
train_data.groupby('label').agg({'label': 'count'}).show()


# In[53]:


test_data.groupby('label').agg({'label': 'count'}).show()			


# In[54]:


# build the logistic regressor
from pyspark.ml.classification import LogisticRegression


# In[55]:


# Initialize `lr`
lr = LogisticRegression(labelCol="label",
                        featuresCol="features",
                        maxIter=10,
                        regParam=0.3)


# In[56]:


# Fit the data to the model
linearModel = lr.fit(train_data)


# In[57]:


# Print the coefficients and intercept for logistic regression
print("Coefficients: " + str(linearModel.coefficients))
print("Intercept: " + str(linearModel.intercept))


# In[58]:


# 5) Train and evaluate the model
# Make predictions on test data using the transform() method.
predictions = linearModel.transform(test_data)


# In[59]:


predictions.printSchema()


# In[60]:


selected = predictions.select("label", "prediction", "probability")
selected.show(20)


# In[61]:


# evaluate the model

# create a data frame with the label and the prediction
cm = predictions.select("label", "prediction")			


# In[62]:


# You can check the number of class in the label and the prediction
cm.groupby('label').agg({'label': 'count'}).show()			


# In[63]:


cm.groupby('prediction').agg({'prediction': 'count'}).show()			


# In[64]:


# You can compute the accuracy
cm.filter(cm.label == cm.prediction).count() / cm.count()			


# In[65]:


def accuracy_m(model): 
    predictions = model.transform(test_data)
    cm = predictions.select("label", "prediction")
    acc = cm.filter(cm.label == cm.prediction).count() / cm.count()
    print("Model accuracy: %.3f%%" % (acc * 100)) 


# In[66]:


accuracy_m(model = linearModel)


# In[67]:


# ROC metrics -- 
from pyspark.ml.evaluation import BinaryClassificationEvaluator


# In[68]:


# Evaluate model
evaluator = BinaryClassificationEvaluator(rawPredictionCol="rawPrediction")
print(evaluator.evaluate(predictions))
print(evaluator.getMetricName())


# In[69]:


print(evaluator.evaluate(predictions))			


# In[70]:


# Tune the Hyperparameter
from pyspark.ml.tuning import ParamGridBuilder, CrossValidator


# In[71]:


# Create ParamGrid for Cross Validation
paramGrid = (ParamGridBuilder()
             .addGrid(lr.regParam, [0.01, 0.5])
             .build())


# In[72]:


# evaluate the model with using the cross valiation method with 5 folds. 
# It takes around 16 minutes to train

from time import *
start_time = time()


# In[73]:


# Create 5-fold CrossValidator
cv = CrossValidator(estimator=lr,
                    estimatorParamMaps=paramGrid,
                    evaluator=evaluator, numFolds=5)


# In[74]:


# Run cross validations
cvModel = cv.fit(train_data)
# likely take a fair amount of time
end_time = time()
elapsed_time = end_time - start_time
print("Time to train model: %.3f seconds" % elapsed_time)


# In[75]:


accuracy_m(model = cvModel)


# In[76]:


# exctract the recommended parameter


# In[77]:


bestModel = cvModel.bestModel
bestModel.extractParamMap()


# In[ ]:




