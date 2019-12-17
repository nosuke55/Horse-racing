import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

"""
11月2日に行われた競馬をトレインして、11月3日に行われた競技をテストしている。
着順が1位以外は0としている。
"""

# split the dataset into training and testing set
keibaData = pd.read_csv("keiba.csv",sep=",")

keibaData1102 = keibaData[0:88]
keibaData1103 = keibaData[89:162]

#X = keibaData.drop(columns='着順').drop(columns='馬名').drop(columns='性齢').drop(columns='騎手').drop(columns='調教師').drop(columns='風向').drop(columns='日時')
#keibaData.loc[keibaData['着順'] != 1, '着順'] = 0
#y = keibaData['着順']

#X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.1,random_state=None)

X_train = keibaData1102.drop(columns='着順').drop(columns='馬名').drop(columns='性齢').drop(columns='騎手').drop(columns='調教師').drop(columns='風向').drop(columns='日時')
keibaData1102.loc[keibaData1102['着順'] != 1, '着順'] = 0
y_train = keibaData1102['着順']

X_test = keibaData1103.drop(columns='着順').drop(columns='馬名').drop(columns='性齢').drop(columns='騎手').drop(columns='調教師').drop(columns='風向').drop(columns='日時')
keibaData1103.loc[keibaData1103['着順'] != 1, '着順'] = 0
y_test = keibaData1103['着順']

# Create linear regression object
regr = LogisticRegression()

# Train the model using the training set
regr.fit(X_train, y_train)

# Make predictions using the testing set
predicted = regr.predict(X_test)

# Check accuracy
print(accuracy_score(y_test, predicted))

mat = confusion_matrix(y_test, regr.predict(X_test))
print(mat)