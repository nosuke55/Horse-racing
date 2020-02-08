# Horse-racing
競馬の予測を機械学習でやってみる  


## ディレクトリ構成
- data CSVファイル
    - Learning_datas : 学習用データ
    - Forecast_datas : 予測用データ
    - Preprocessed_datas : 前処理済みデータ
    - lgb_model : LightGBMモデルの保存場所
- src ソースコード 


## 開発環境
- Python: 3.7.6
- MacOS Catalina 10.15.3

## パッケージリスト
- Numpy: 1.16.0
- Pandas: 0.25.3
- Optuna: 0.19.0
- LightGBM: 2.3.1
- Selenium: 3.141.0
- Chromedriver-binary: 79.0.3945.36.0

## スクレイピング 
1. 学習用データの取得
学習用にこれまで行われた競馬の結果を取得する。
`python3 scraping.py`
スクレイピング後にCSVファイルの作成。
`python3 make_csv.py`

2. 予測用データの取得
その日行われる競馬の出馬情報の取得。
`python3 newscraping.py`


## 競馬学習
`python3 keiba.py`で学習を始めることができる。
~~~Python
if __name__ == "__main__":
    # インスタンス生成
    lgb = LightGBM()

    train_csv_name = "train_2019_3"
    test_csv_name = "test_2019_3"
    # test_csvが予測したいレースの場合 True, 新しいモデルを作成したい場合 False
    yosoku = False
~~~

## 競馬予想
学習と同じように`python3 keiba.py`で未知のデータに対する予測をすることができる。だが、`keiba.py`の中身を少し書き換える必要がある。
~~~Python
if __name__ == "__main__":
    # インスタンス生成
    lgb = LightGBM()

    train_csv_name = "train_2019_3"
    test_csv_name = "arima.csv"
    # test_csvが予測したいレースの場合 True, 新しいモデルを作成したい場合 False
    yosoku = True
~~~