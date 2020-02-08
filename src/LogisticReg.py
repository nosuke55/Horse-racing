from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
import category_encoders as ce
import numpy as np
import pandas as pd

class LogisticReg():
    def __init__(self, solver='lbfgs', max_iter=1000, penalty='l2', dual=False, tol=0.0001, C=1.0,
                fit_intercept=True, intercept_scaling=1, class_weight=None, random_state=None,
                multi_class='warn', verbose=0, warm_start=False, n_jobs=None):
        self.model = LogisticRegression(solver=solver, max_iter=max_iter, penalty=penalty, dual=dual, tol=tol, C=C,
                                        fit_intercept=fit_intercept, intercept_scaling=intercept_scaling, class_weight=class_weight, random_state=random_state,
                                        multi_class=multi_class, verbose=verbose, warm_start=warm_start, n_jobs=n_jobs)

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
        #newColumns = ["Win_or_Lose", "Frame", "Horse_Num", "Horse_Name", "Sex_Age", "Burden_Weight", "Jockey", "Estimated_Climb",
        #    "Horse_Weight", "Weight_Gain_or_Loss", "Trainer", "Winning_Popularity", "Precipitation_Amount", "Temperature", 
        #    "Wind_Speed", "Wind_Direction", "Race", "Distance", "Date", "Frame2", "Horse_Num2", "Horse_Name2", "Sex_Age2", 
        #    "Burden_Weight2", "Jockey2", "Estimated_Climb2", "Horse_Weight2", "Weight_Gain_or_Loss2", "Trainer2", "Winning_Popularity2", 
        #    "Precipitation_Amount2", "Temperature2", "Wind_Speed2", "Wind_Direction2", "Race2", "Distance2", "Date2"]
        newColumns = ["Win_or_Lose", "Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Horse_Weight", "Weight_Gain_or_Loss", "Trainer",
                     "Jockey","Burden_Weight", "Winning_Popularity", "Estimated_Climb", "Frame2", "Horse_Num2", "Horse_Name2", "Sex2","Age2",
                     "Horse_Weight2", "Weight_Gain_or_Loss2", "Trainer2", "Jockey2","Burden_Weight2", "Winning_Popularity2", "Estimated_Climb2"]
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

    # 学習
    def fit(self, X_train, y_train):
        self.model.fit(X_train, y_train)

    def predict(self,X_test):
        return self.model.predict(X_test)

    def accuracy_matrix(self, X_test, y_test):
        mat = confusion_matrix(y_test, self.model.predict(X_test))
        print("正解率\n",mat)

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