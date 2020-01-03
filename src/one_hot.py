import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

keibaData = pd.read_csv("keiba.csv",sep=",")
keibaData.head()

from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder

#uma_name = keibaData['馬名'].values
#uma_name_enc = preprocessing.LabelEncoder().fit_transform(uma_name).reshape(-1,1)
#uma_name_enc2 = OneHotEncoder().fit_transform(uma_name_enc).toarray()

#kisyu_name = keibaData['騎手'].values
#kisyu_name_enc = preprocessing.LabelEncoder().fit_transform(kisyu_name).reshape(-1,1)
#kisyu_name_enc2 = OneHotEncoder().fit_transform(kisyu_name_enc).toarray()

SM_name = keibaData['調教師'].values
SM_name_enc = preprocessing.LabelEncoder().fit_transform(SM_name).reshape(-1,1)
SM_name_enc2 = OneHotEncoder().fit_transform(SM_name_enc).toarray()
#df = keibaData.assign(SM_name_enc2)

print(SM_name_enc2)
