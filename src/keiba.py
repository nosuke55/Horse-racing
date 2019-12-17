import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

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
    newColumns = ["勝負", "枠", "馬番", "馬名", "負担重量", "推定上り", "馬体重", "増減", "単勝人気", 
        "降水量", "気温", "風速", "レース", "距離", "枠2", "馬番2", "馬名2", "負担重量2", "推定上り2", 
        "馬体重2", "増減2", "単勝人気2", "降水量2", "気温2", "風速2", "レース2", "距離2"]
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
    newData = pd.DataFrame(merge, index=None, columns=newColumns)
    #newData.to_csv("test.csv", encoding="utf-8-sig") # csvで書き出し
    return newData

if __name__ == "__main__":
    keibaData = pd.read_csv("../data/201911.csv",sep=",")
    keibaData = preprocessing(keibaData)
    X = keibaData.drop(columns=['勝負', '馬名', '馬名2'])
    y = keibaData['勝負']
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.1,random_state=0)
    fit(X_train, y_train, X_test, y_test)