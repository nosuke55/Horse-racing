#lightgbmのイストール必須
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn import metrics
import category_encoders as ce
from tqdm import tqdm
from sklearn import preprocessing #カテゴリデータ(定性的データ)を辞書順に整数に変換
import matplotlib.pyplot as plt


#ふうう
class LightGBM():
    # 初期処理
    def __init__(self, boostring='dart' , learning_rate=0.05, min_data_in_leaf=20,#applications='binary'
        feature_fraction=0.7,num_leaves=41, metric='auc', drop_date=0.15):
        self.parameters = {
            'boosting': boostring,          # dart (drop out trees) often performs better
            #'application': applications,     # Binary classification
            'learning_rate': learning_rate,       # Learning rate, controls size of a gradient descent step
            'min_data_in_leaf': min_data_in_leaf,      # Data set is quite small so reduce this a bit
            'feature_fraction': feature_fraction,     # Proportion of features in each boost, controls overfitting
            'num_leaves': num_leaves,            # Controls size of tree since LGBM uses leaf wise splits
            'metric': metric,  # Area under ROC curve as the evaulation metric
            'drop_rate': drop_date   
        }
        self.evaluation_results = {}
        self.model = lgb.LGBMModel()

    # 競馬用 前処理
    def preprocessing(self, keibaData):
        """レースごとの馬の組み合わせ作成

        入力のレース情報にいる馬同士の組み合わせを作成する。
        組み合わせ作成後は順位データは削除され、馬同士の勝ち負けが追加される。

            Args:
                keibaData(pd.DataFrame):
                    レースの情報。CSVファイル等から読み込んだデータ。順位の情報が必須であり1番目のカラムにある必要がある。
            
            Returns:
                newData(pd.DataFrame):
                    馬の組み合わせ情報。``Win_or_Lose``カラムが組み合わせの勝ち負け。前の馬が後ろの馬に勝っていれば1、負けなら0。
            
            Note:
                newColumns(list)は引数のkeibaData(pd.DataFrame)のカラムを2つ繋げたものとなる。
                そのため、keibaDataから削除したカラム、追加したカラムがあればnewColumnsも合わせる必要がある。

        """
        # コース情報や気象情報などがない時のカラム
        #newColumns = ["Win_or_Lose", "Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Horse_Weight", "Weight_Gain_or_Loss", "Trainer",
        #             "Jockey","Burden_Weight", "Winning_Popularity", "Estimated_Climb", "Frame2", "Horse_Num2", "Horse_Name2", "Sex2","Age2",
        #             "Horse_Weight2", "Weight_Gain_or_Loss2", "Trainer2", "Jockey2","Burden_Weight2", "Winning_Popularity2", "Estimated_Climb2"]
        # コース情報や気象情報がある時のカラム
        #newColumns = ["Win_or_Lose", "Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Horse_Weight", "Weight_Gain_or_Loss", "Trainer", "Jockey",
        #              "Burden_Weight", "Winning_Popularity", "Estimated_Climb", "date", "course", "meter", "direction", "weather", "status",
        #              "Frame2", "Horse_Num2", "Horse_Name2", "Sex2","Age2", "Horse_Weight2", "Weight_Gain_or_Loss2", "Trainer2", "Jockey2", 
        #              "Burden_Weight2", "Winning_Popularity2", "Estimated_Climb2", "date2","course2", "meter2", "direction2", "weather2", "status2"]
        # 単勝人気を消したカラム
        newColumns = ["Win_or_Lose", "Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Horse_Weight", "Weight_Gain_or_Loss", "Trainer", "Jockey",
                      "Burden_Weight", "Estimated_Climb", "date", "course", "meter", "direction", "weather", "status",
                      "Frame2", "Horse_Num2", "Horse_Name2", "Sex2","Age2", "Horse_Weight2", "Weight_Gain_or_Loss2", "Trainer2", "Jockey2", 
                      "Burden_Weight2", "Estimated_Climb2", "date2","course2", "meter2", "direction2", "weather2", "status2"]
        # 単勝人気、推定上がりを消したカラム
        #newColumns = ["Win_or_Lose", "Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Horse_Weight", "Weight_Gain_or_Loss", "Trainer", "Jockey",
        #              "Burden_Weight", "date", "course", "meter", "direction", "weather", "status",
        #              "Frame2", "Horse_Num2", "Horse_Name2", "Sex2","Age2", "Horse_Weight2", "Weight_Gain_or_Loss2", "Trainer2", "Jockey2", 
        #              "Burden_Weight2", "date2","course2", "meter2", "direction2", "weather2", "status2"]
        horse_merge = []
        delete = 0 # 次に削除する最初の番地の保持。
        rtime = tqdm(total=len(keibaData)) # ランタイム。 ターミナル上に前処理の進捗状況を表示する。
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
                    front_horse = np.delete(races[i], 0) # 順位の削除
                    back_horse = np.delete(races[j], 0) # 順位の削除
                    horses = np.concatenate([front_horse, back_horse]) # 2行を結合する。
                    horses = np.insert(horses, 0, wl) # 最初に勝負を追加する。
                    horse_merge.append(list(horses))
                    # 上の追加の逆をする。 例: 上が勝ちパターンなら負けパターン
                    if wl == 1: wl = 0
                    else: wl = 1
                    horses = np.concatenate([back_horse, front_horse]) # 2行を結合する。
                    horses = np.insert(horses, 0, wl) # 最初に勝負を追加する。
                    horse_merge.append(list(horses))
            rtime.update(len(races)) # ランタイムの更新
        newData = pd.DataFrame(horse_merge, index=None, columns=newColumns, dtype='float64')
        return newData

    # 文字データの処理
    def category_encode(self, keibaTrain, keibaTest, category):
        """カテゴリ特徴量の処理

        ``Category encoders``の``OrdinalEncoder``で処理をする。

            Args:
                keibaTrain(pd.DataFrame):
                    学習用のトレーニングデータ
                keibaTest(pd.DataFrame):
                    学習用のテストデータ
                category(list):
                    カテゴリデータの一覧(カラム名)。
            
            Returns:
                train, test(pd.DataFrame):
                    カテゴ特徴量の処理後。

        """
        ce_oe = ce.OrdinalEncoder(cols=category,handle_unknown='value')
        train = ce_oe.fit_transform(keibaTrain)
        test = ce_oe.transform(keibaTest)
        return train, test

    # 学習データ作成
    def train_data(self, X_train, y_train):
        return lgb.Dataset(X_train, label=y_train)
    
    # テストデータの作成
    def test_data(self, X_test, y_test, train_data):
        return lgb.Dataset(X_test, label=y_test, reference=train_data)

    # 学習
    def fit(self, train_data, test_data, batch=100):
        #evaluation_results = {}
        self.model=lgb.train(self.parameters,
                        train_data,
                        valid_sets=[train_data, test_data], 
                        valid_names=['Train', 'Test'],
                        evals_result = self.evaluation_results,
                        num_boost_round=batch,
                        early_stopping_rounds=50,
                        verbose_eval=20)
        optimum_boost_rounds = self.model.best_iteration
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
        """予測後の順位を表示する

            Args:
                keibaTest(pd.DataFrame):
                    学習で使用したテストデータ。``preprocessing``関数の処理後のデータであり、カテゴリ処理をしていないデータである必要がある。
                predicted(list):
                    学習後のpredicted。``predict``関数で取得できる。
            
            Note:
                馬の組み合わせを作成したデータから、predictedで勝ちと予想された行を取り出し、馬名をカウントしている。
                そのため、馬の組み合わせ処理が必要であり``preprocessing``関数を利用したデータのみ表示することができる。

        """
        rank = pd.DataFrame()
        # predicted で勝ちと予想された行のみを取得
        for p in range(0, len(predicted), 2):
            if predicted[p] > predicted[p+1]:
                rank = rank.append(keibaTest.iloc[p])
            else:
                rank = rank.append(keibaTest.iloc[p+1])
        # 勝率順 - 馬名を馬ごとにカウントする
        print(rank['Horse_Name'].value_counts())
    
    #重要度の可視化
    def plot_imp(self):
        fig, axs = plt.subplots(2, 1, figsize=[20, 10])

        # Plot the log loss during training
        axs[0].plot(self.evaluation_results['Train']['auc'], label='Train')
        axs[0].plot(self.evaluation_results['Test']['auc'], label='Test')
        axs[0].set_ylabel('auc')
        axs[0].set_xlabel('Boosting round')
        axs[0].set_title('Training performance')
        axs[0].legend()

        # Plot feature importance
        importances = pd.DataFrame({'features': self.model.feature_name(), 
                                    'importance': self.model.feature_importance()}).sort_values('importance', ascending=False)
        axs[1].bar(x=np.arange(len(importances)), height=importances['importance'])
        axs[1].set_xticks(np.arange(len(importances)))
        axs[1].set_xticklabels(importances['features'])
        axs[1].set_ylabel('Feature importance (# times used to split)')
        axs[1].set_title('Feature importance')

        plt.xticks(rotation=90)
        plt.tight_layout()
        #plt.show()
        plt.savefig("重要度.png")
