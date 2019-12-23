import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from LightGBM import LightGBM#自作classのimport
import lightgbm as lgb
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score

# 学習する
def fit(X_train, y_train, X_test, y_test):
    # Create linear regression object
    regr = LogisticRegression(solver='lbfgs', max_iter=1000)
    # Train the model using the training set
    regr.fit(X_train, y_train)
    # Make predictions using the testing set
    predicted = regr.predict(X_test)
    # Check accuracy
    print(accuracy_score(y_test, predicted))
    mat = confusion_matrix(y_test, regr.predict(X_test))
    print(mat)

# 前処理
def preprocessing(keibaData):
    dropdData = keibaData.drop(['性齢', '騎手', '調教師', '風向', '日時'], axis=1)
    newColumns = ["label", "frame", "horse_num", "horse_name", "burden_weight", "estimated_rise", "horse_weight", "fluctuation", "winning_popularity", 
        "precipitation_amount", "temperature", "wind_speed", "rase", "distance", "frame2", "horse_num2", "horse_name2", "burden_weight2", "estimated_rise2", 
        "horse_weight2", "fluctuation2", "winning_popularity2", "precipitation2", "temperature2", "wind_speed2", "rase2", "deistance2"]
    merge = []
    delete = 0 # 次に削除する最初の番地の保持。
    while len(dropdData) != 0:
        Datas = []
        # 1レース分の取得
        for race in range(len(dropdData.values)):
            Datas.append(list(dropdData.values[race]))
            try:
                if dropdData.values[race+1][0] == 1:
                    break
            except IndexError: # 最後のレースの場合。(次のレースがない)
                break
        # 取得した分を削除する
        dropdData = dropdData.drop(list(range(delete,len(Datas)+delete)))
        delete += len(Datas)
        # パターン作成
        for i in range(len(Datas)):
            for j in range(i+1, len(Datas)):
                if Datas[i][0] < Datas[j][0]: wl = 1 # 勝ち
                else: wl = 0 # 負け
                maeUma = np.delete(Datas[i], 0)
                usiUma = np.delete(Datas[j], 0)
                gyou = np.concatenate([maeUma, usiUma])
                gyou = np.insert(gyou, 0, wl)
                merge.append(list(gyou))
                # 上の追加の逆をする。 例: 上が勝ちパターンなら負けパターン
                if wl == 1: wl = 0
                else: wl = 1
                gyou = np.concatenate([usiUma, maeUma])
                gyou = np.insert(gyou, 0, wl)
                merge.append(list(gyou))
    newData = pd.DataFrame(merge, index=None, columns=newColumns,dtype='float64')
    #newData.to_csv("test.csv", encoding="utf-8-sig") # csvで書き出し
    return newData

if __name__ == "__main__":
    lgbm=LightGBM()
    keibaData = pd.read_csv("../data/201911.csv",sep=",")
    keibaData = preprocessing(keibaData)
    #keibaData.columns = ['a', 'b', 'c']
    X = keibaData.drop(columns=['label', 'horse_name', 'horse_name2'])#label,horse_name,horse_name2
    y = keibaData['label']
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.1,random_state=0)
    print(X)
    #fit(X_train, y_train, X_test, y_test)
    hp=lgbm.hyperparm()
    train_data=lgbm.train_data(X_train,y_train,lgb)
    test_data=lgbm.test_data(X_test,y_test,train_data,lgb)
    model=lgbm.fit(hp,train_data,test_data,lgb)
    y_pred=lgbm.predict(X_test,model)
    lgbm.accuracy_rate(y_test,y_pred)
    #print("正解率",accuracy_score(y_test, y_pred))
    #mat = confusion_matrix(y_test, y_pred)
    y_pred_list = []
    for x in y_pred:
        y_pred_list.append(np.argmax(x))
    mat = confusion_matrix(y_test, y_pred_list)
    print(mat)
    #print(y_test)
    print('Accuracy score = \t {}'.format(accuracy_score(y_test, y_pred_list)))
    print('Precision score = \t {}'.format(precision_score(y_test, y_pred_list)))
    print('Recall score =   \t {}'.format(recall_score(y_test, y_pred_list)))
    print('F1 score =      \t {}'.format(f1_score(y_test, y_pred_list)))
