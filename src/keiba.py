import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

# 学習する
def fit(X_train, y_train, X_test, y_test):
    """
    2019/12/21
    ・学習する関数。
    ・modelはLogisticRegressionを使用。今のところLinearSVC, RandomForestClassifierより精度良かった。
    ・まぁパラメーター何もいじってないんですけどね...
    ・学習後に正答率と混合行列を表示する。
    """
    # Create linear regression object
    regr = LogisticRegression(solver='lbfgs', max_iter=1000)
    # Train the model using the training set
    regr.fit(X_train, y_train)
    # Make predictions using the testing set
    predicted = regr.predict(X_test)
    # Check accuracy
    print(accuracy_score(y_test, predicted))
    #print(predicted)
    mat = confusion_matrix(y_test, regr.predict(X_test))
    print(mat)
    return predicted

# 前処理
def preprocessing(keibaData):
    """
    2019/12/21
    ・現時点では馬名以外の文字が含まれる列はすべて除去している。
    ・除去しない場合は、dropをさせないのとnewColumnsにカラム名を追加する必要あり。
    ・この前処理では、csvファイルを全て入れる必要がある。
    例
    ・1つのcsvのデータを11日だけを前処理, 12日だけを前処理などはできない。
    """
    dropdData = keibaData #.drop(['性齢', '騎手', '調教師', '風向', '日時'], axis=1)
    newColumns = ["勝負", "枠", "馬番", "馬名", "性齢", "負担重量", "騎手", "推定上り", "馬体重", "増減", "調教師", "単勝人気", 
        "降水量", "気温", "風速", "風向", "レース", "距離", "日時", "枠2", "馬番2", "馬名2", "性齢2", "負担重量2", "騎手2", "推定上り2", 
        "馬体重2", "増減2", "調教師2", "単勝人気2", "降水量2", "気温2", "風速2", "風向2", "レース2", "距離2", "日時2"]
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

# One-hotエンコーディング。 日本語の部分をOne-hotで表す
def one_hot(keibaData):
    return pd.get_dummies(keibaData, columns=['馬名', '性齢', '騎手', '調教師', '風向', '日時', 
        '馬名2', '性齢2', '騎手2', '調教師2', '風向2', '日時2'])

# 馬の順位を表示する
def ranking(keibaTest, predicted):
    """
    馬の順位を表示する。
    馬ごとにカウントする。そのため一番カウントが多い馬が1位と予想される。
    """
    rank = pd.DataFrame()
    # predicted で勝ちと予想された行のみを取得
    for p in range(len(predicted)):
        if predicted[p] == '1':
            rank = rank.append(keibaTest.iloc[p])
    # 勝率順 - 馬名を馬ごとにカウントする
    print(rank['馬名'].value_counts())

if __name__ == "__main__":
    # csvを読み込む
    keibaTrain = pd.read_csv("../data/201910-11.csv",sep=",")
    keibaTest = pd.read_csv("../data/arima2.csv",sep=",", encoding='shift-jis')

    # トレインデータの前処理
    keibaTrain = preprocessing(keibaTrain)
    #keibaTrain = one_hot(keibaTrain)

    # テストデータの前処理
    keibaTest = preprocessing(keibaTest)
    keibaTest2 = keibaTest.copy() # rankingの表示用
    #keibaTest = one_hot(keibaTest)
    # 次元合わせ
    #keibaTest = keibaTest.reindex(labels=keibaTrain.columns,fill_value=0, axis=1)

    # データの準備
    #X_train = keibaTrain.drop(columns="勝負")
    X_train = keibaTrain.drop(columns=['勝負', '馬名', '性齢', '騎手', '調教師', '風向', '日時', '馬名2', '性齢2', '騎手2', '調教師2', '風向2', '日時2'])
    y_train = keibaTrain["勝負"]

    #X_test = keibaTest.drop(columns="勝負")
    X_test = keibaTest.drop(columns=['勝負', '馬名', '性齢', '騎手', '調教師', '風向', '日時', '馬名2', '性齢2', '騎手2', '調教師2', '風向2', '日時2'])
    y_test = keibaTest["勝負"]

    # 学習する
    predicted = fit(X_train, y_train, X_test, y_test)
    # 順位を表示する
    ranking(keibaTest2, predicted)