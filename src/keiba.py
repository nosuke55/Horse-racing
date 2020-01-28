import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score
import optuna
from functools import partial
from LightGBM import LightGBM
#from LogisticReg import LogisticReg
import pickle, os

# ハイパーパラメータ関数
def objective(trial, X_train, y_train, X_test, y_test, batch=100):
    """最小化する目的関数"""
    # 調整するハイパーパラメータ
    params = {
        'boostring': trial.suggest_categorical('boostring', ['gbdt', 'dart', 'goss']),
        'metric': {'binary', 'binary_error', 'auc'},
        'num_leaves': trial.suggest_int("num_leaves", 10, 500),
        'learning_rate': trial.suggest_loguniform("learning_rate", 1e-5, 1),
        'feature_fraction': trial.suggest_uniform("feature_fraction", 0.0, 1.0),
        'min_data_in_leaf': int(trial.suggest_int('min_data_in_leaf', 2, 64))
    }
    
    #params = {
    #    'learning_rate': trial.suggest_uniform('learning_rate', 1e-2, 1e0),
    #    'min_data_in_leaf': int(trial.suggest_int('min_data_in_leaf', 2, 64)),
    #    'feature_fraction': trial.suggest_uniform('feature_fraction', 1e-1, 1e0),
    #    'num_leaves':int(trial.suggest_int('num_leaves', 2, 128)),
    #    'drop_date': trial.suggest_uniform('drop_date', 1e-2, 1e0),
    #}

    #model = xgb.XGBClassifier(**params, boosting='dart', application='binary',metric='auc')
    lgb = LightGBM(**params)
    lgb.fit(X_train,y_train, batch=batch) # 学習させる
    pred = lgb.predict(X_test)  # テストデータからラベルを予測する
    preds = np.round(np.abs(pred))
    return f1_score(y_true=y_test, y_pred=preds, average='micro')#accuracy_score(y_test, model.predict(X_test))#最小化なので1から正解率を引く

def create_new_model(keibaTrain, keibaTest, n_trials=30, batch=100):
    # インスタンス生成
    lgb = LightGBM()
    # データの準備
    X_train = keibaTrain.drop(columns="Win_or_Lose")
    y_train = keibaTrain["Win_or_Lose"]
    horse_Train = lgb.train_data(X_train, y_train)

    X_test = keibaTest.drop(columns="Win_or_Lose")
    y_test = keibaTest["Win_or_Lose"]
    horse_Test = lgb.test_data(X_test, y_test, horse_Train)

    #ハイパーパラメータ探索
    study = optuna.create_study(direction='maximize')  # 最適化のセッションを作る,minimize,maximize
    study.optimize(lambda trial: objective(trial, horse_Train, horse_Test, X_test, y_test, batch), n_trials=n_trials)  # 最適化のセッションを作る
    print("ベストF１",study.best_value)
    print("ベストparam", study.best_params)

    # ベストパラメータで学習。 学習後モデルを保存する。
    lgb = LightGBM(**study.best_params)
    lgb.fit(horse_Train, horse_Test, batch=batch)
    if not os.path.exists("../data/lgb_model"):
        os.mkdir("../data/lgb_model")
    with open("../data/lgb_model/bestModel.pkl", "wb") as fp:
        pickle.dump(lgb.model, fp)

def load_model(keibaTest, keibaRank):
    # インスタンス生成
    lgb = LightGBM()

    with open("../data/lgb_model/bestModel.pkl", "rb") as pkl:
        lgb.model = pickle.load(pkl)

    # データの準備
    X_test = keibaTest.drop(columns="Win_or_Lose")
    y_test = keibaTest["Win_or_Lose"]

    # モデルと比較
    predicted = lgb.predict(X_test)
    lgb.accuracy_rate(y_test, predicted)
    # 順位を表示する
    lgb.ranking(keibaTest2, predicted)
    lgb.plot_imp()

def load_csv(train_csv_name, test_csv_name, yosoku=False):
    """
    データの置き方。
    学習データは data/Learning_datas内に保存する。
    予想データは data/Forecast_datas内に保存する。
    前処理済みデータは data/Preprocessed_datas内に保存する。
    """
    train_pre, test_pre = False, False
    if os.path.exists("../data/Preprocessed_datas/"+train_csv_name+"_preprocessing.csv"):
        train_csv_path = "../data/Preprocessed_datas/"+train_csv_name+"_preprocessing.csv"
    else:
        train_csv_path = "../data/Learning_datas/"+train_csv_name+".csv"
        train_pre = True
    
    if os.path.exists("../data/Preprocessed_datas/"+test_csv_name+"_preprocessing.csv"):
        test_csv_path = "../data/Preprocessed_datas/"+test_csv_name+"_preprocessing.csv"
    else:
        if yosoku:
            test_csv_path = "../data/Forecast_datas/"+test_csv_name+".csv"
        else:
            test_csv_path = "../data/Learning_datas/"+test_csv_name+".csv"
        test_pre = True
    try:
        keibaTrain = pd.read_csv(train_csv_path, sep=",")
    except UnicodeDecodeError:
        keibaTrain = pd.read_csv(train_csv_path, sep=",", encoding="shift-jis")
    try:
        keibaTest = pd.read_csv(test_csv_path, sep=",")
    except UnicodeDecodeError:
        keibaTest = pd.read_csv(test_csv_path, sep=",", encoding="shift-jis")
    # Unnamed: 0の削除。　preprocessing後のデータについてる
    try:
        keibaTrain = keibaTrain.drop(columns="Unnamed: 0")
    except KeyError:
        pass
    try:
        keibaTest = keibaTest.drop(columns="Unnamed: 0")
    except KeyError:
        pass
    return keibaTrain, train_pre, keibaTest, test_pre  

if __name__ == "__main__":
    # インスタンス生成
    lgb = LightGBM()

    train_csv_name = "train_2019_2"
    test_csv_name = "test_2019_2"
    # test_csvが予測したいレースの場合 True, 新しいモデルを作成したい場合 False
    yosoku = False

    # csvを読み込む
    print("Load csv... ", end='')
    keibaTrain, train_pre, keibaTest, test_pre = load_csv(train_csv_name, test_csv_name, yosoku=yosoku)
    print(" done.")

    # 前処理
    if train_pre:
        print("Train preprocessing... ")
        keibaTrain = lgb.preprocessing(keibaTrain)
        keibaTrain.to_csv("../data/Preprocessed_datas/"+train_csv_name+"_preprocessing.csv", encoding="shift-jis")

    if test_pre:
        print("Test preprocessing... ")
        keibaTest = lgb.preprocessing(keibaTest)
        keibaTest.to_csv("../data/Preprocessed_datas/"+test_csv_name+"_preprocessing.csv", encoding="shift-jis")

    # ランキング表示させるなら。
    keibaTest2 = keibaTest.copy() # rankingの表示用

    # カテゴリー処理
    category = ["Horse_Name", "Sex", "Jockey", "Trainer", "date", "course", "direction", "weather", "status",
                "Horse_Name2", "Sex2", "Jockey2", "Trainer2", "date2", "course2", "direction2", "weather2", "status2"]
    #category = ["Horse_Name", "Sex", "Jockey", "Trainer",
    #            "Horse_Name2", "Sex2", "Jockey2", "Trainer2"]
    keibaTrain, keibaTest = lgb.category_encode(keibaTrain, keibaTest, category)

    if yosoku:
        load_model(keibaTest, keibaTest2)
    else:
        create_new_model(keibaTrain, keibaTest, n_trials=30, batch=100)
