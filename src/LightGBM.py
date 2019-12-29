#lightgbmのイストール必須
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn import metrics
import category_encoders as ce
#ふうう
class LightGBM():
        # 初期処理
    def __init__(self, boostring='dart', applications='binary', learning_rate=0.05, min_data_in_leaf=20,
        feature_fraction=0.7,num_leaves=41, metric='auc', drop_date=0.15):
        self.parameters = {
            'boosting': boostring,          # dart (drop out trees) often performs better
            'application': applications,     # Binary classification
            'learning_rate': learning_rate,       # Learning rate, controls size of a gradient descent step
            'min_data_in_leaf': min_data_in_leaf,      # Data set is quite small so reduce this a bit
            'feature_fraction': feature_fraction,     # Proportion of features in each boost, controls overfitting
            'num_leaves': num_leaves,            # Controls size of tree since LGBM uses leaf wise splits
            'metric': metric,  # Area under ROC curve as the evaulation metric
            'drop_rate': drop_date   
        }
        self.model = "model in here"

    # 競馬用 前処理
    def preprocessing(self, keibaData):
        newColumns = ["Win_or_Lose", "Frame", "Horse_Num", "Horse_Name", "Sex_Age", "Burden_Weight", "Jockey", "Estimated_Climb",
            "Horse_Weight", "Weight_Gain_or_Loss", "Trainer", "Winning_Popularity", "Precipitation_Amount", "Temperature", 
            "Wind_Speed", "Wind_Direction", "Race", "Distance", "Date", "Frame2", "Horse_Num2", "Horse_Name2", "Sex_Age2", 
            "Burden_Weight2", "Jockey2", "Estimated_Climb2", "Horse_Weight2", "Weight_Gain_or_Loss2", "Trainer2", "Winning_Popularity2", 
            "Precipitation_Amount2", "Temperature2", "Wind_Speed2", "Wind_Direction2", "Race2", "Distance2", "Date2"]
        horse_merge = []
        delete = 0 # 次に削除する最初の番地の保持。
        while len(keibaData) != 0:
            races = []
            # 1レース分の取得
            for race in range(len(keibaData.values)):
                races.append(list(keibaData.values[race]))
                try:
                    if keibaData.values[race+1][0] == 1:
                        break
                except IndexError: # 最後のレースの場合。(次のレースがない)
                    break
            # 取得した分を削除する
            keibaData = keibaData.drop(list(range(delete,len(races)+delete)))
            delete += len(races)
            # パターン作成
            for i in range(len(races)):
                for j in range(i+1, len(races)):
                    if races[i][0] < races[j][0]: wl = 1 # 勝ち
                    else: wl = 0 # 負け
                    front_horse = np.delete(races[i], 0)
                    back_horse = np.delete(races[j], 0)
                    horses = np.concatenate([front_horse, back_horse]) # 2行を結合する。
                    horses = np.insert(horses, 0, wl) # 最初に勝負を追加する。
                    horse_merge.append(list(horses))
                    # 上の追加の逆をする。 例: 上が勝ちパターンなら負けパターン
                    if wl == 1: wl = 0
                    else: wl = 1
                    horses = np.concatenate([back_horse, front_horse]) # 2行を結合する。
                    horses = np.insert(horses, 0, wl) # 最初に勝負を追加する。
                    horse_merge.append(list(horses))
        newData = pd.DataFrame(horse_merge, index=None, columns=newColumns, dtype='float64')
        return newData 

    # 文字データの処理
    def category_encode(self, keibaData, category):
        ce_oe = ce.OrdinalEncoder(cols=category,handle_unknown='impute')
        return ce_oe.fit_transform(keibaData)

    # 学習データ作成
    def train_data(self, X_train, y_train):
        return lgb.Dataset(X_train, label=y_train)
    
    # テストデータの作成
    def test_data(self, X_test, y_test, train_data):
        return lgb.Dataset(X_test, label=y_test, reference=train_data)

    # 学習
    def fit(self, train_data, test_data, batch=500):
        evaluation_results = {}
        self.model=lgb.train(self.parameters,
                        train_data,
                        valid_sets=[train_data, test_data], 
                        valid_names=['Train', 'Test'],
                        evals_result=evaluation_results,
                        num_boost_round=batch,
                        early_stopping_rounds=100,
                        verbose_eval=20)
        #optimum_boost_rounds = self.model.best_iteration
        #return optimum_boost_rounds

    def predict(self,X_test):
        return self.model.predict(X_test)

    def accuracy_rate(self,y_test,y_pred):
        fpr, tpr, thresholds = metrics.roc_curve(y_test, y_pred)
        auc = metrics.auc(fpr, tpr)
        print("正解率",auc)
        #return fpr, tpr

    # 馬の順位を表示する
    def ranking(self, keibaTest, predicted):
        rank = pd.DataFrame()
        # predicted で勝ちと予想された行のみを取得
        for p in range(0, len(predicted), 2):
            if predicted[p] > predicted[p+1]:
                rank = rank.append(keibaTest.iloc[p])
            else:
                rank = rank.append(keibaTest.iloc[p+1])
        # 勝率順 - 馬名を馬ごとにカウントする
        print(rank['Horse_Name'].value_counts())