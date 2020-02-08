"""csv変換

``scraping.py``により取得された``data.txt``、``agari.txt``、``race_info.txt``のデータからcsvファイルを作成する。

    Note:
        ``scraping.py``で取得されたテキストデータのみcsv変換が可能である。

"""
import pandas as pd
import re

def csv_generator(data, agari, info):
    """リストデータからcsv作成

        Args:
            data(list), agari(list), info(list):
                ``readTextfiles``関数からのリスト型データ
        
        Note:
            データを追加した場合はcolumnsも更新する必要がある。

    """
    #columns = ["Ranking", "Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Horse_Weight", "Weight_Gain_or_Loss",
    #            "Trainer", "Jockey", "Burden_Weight", "Winning_Popularity", "Estimated_Climb"]
    columns = ["Ranking", "Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Horse_Weight", "Weight_Gain_or_Loss", "Trainer", "Jockey",
               "Burden_Weight", "Winning_Popularity", "Estimated_Climb", "date", "course", "meter", "direction", "weather", "status"]
    merge = []
    zeroAgari = False
    isCancell = False
    for a in agari:
        #if a == "": continue
        if a == "":
            zeroAgari = True
        tmp = []
        while data != []:
            tmp_a = data.pop(0)
            if tmp_a == "中止" or tmp_a == "降":
                while "人気" not in data.pop(0): pass
                isCancell = True
                break
            if tmp_a == "取消" or tmp_a == "除外":
                while "" != data.pop(0): pass
                data.pop(0)
                isCancell = True
                break
            if tmp_a == "着": continue # 着は無視!!
            try:
                if "セ" in tmp_a:
                    sei = tmp_a[0]
                    age = int(tmp_a[1])
                    taiju = int(tmp_a[3:6])
                    zogen = 0
                    if tmp_a[7] == "+": # 増加なら正
                        zogen = int(re.sub("\\D", "", tmp_a[7:]))
                    elif tmp_a[7] == "-": # 減少なら負
                        zogen = -int(re.sub("\\D", "", tmp_a[7:]))
                    tmp += sei, age, taiju, zogen
                    continue
            except ValueError:
                pass
            if "牡" in tmp_a or "牝" in tmp_a: # 性別, 年齢, 体重, 増減に分ける。
                #print(tmp)
                #print(tmp_a)
                sei = tmp_a[0]
                age = int(tmp_a[1])
                taiju = int(tmp_a[3:6])
                zogen = 0
                try:
                    if tmp_a[7] == "+": # 増加なら正
                        zogen = int(re.sub("\\D", "", tmp_a[7:]))
                    elif tmp_a[7] == "-": # 減少なら負
                        zogen = -int(re.sub("\\D", "", tmp_a[7:]))
                except IndexError:
                    pass
                tmp += sei, age, taiju, zogen
                continue
            if ":" in tmp_a: # タイムが来たら、人気倍率まで削除する。
                while "倍" not in data.pop(0): pass # こいつで削除
                continue
            if "(" in tmp_a: # 負担重量の取得
                j = int(re.sub("\\D", "", tmp_a)) / 10
                tmp.append(j)
                continue
            if "人気" in tmp_a: # 単勝人気の取得。取得後whileを抜ける
                tmp.append(re.sub("\\D", "", tmp_a))
                break
            try:
                tmp.append(int(tmp_a)) # 数値はint型に
            except ValueError:
                if tmp_a[0].isalpha(): # 騎手の名前の記号を排除する
                    tmp.append(tmp_a) # 名前はstring型
                else:
                    tmp.append(tmp_a[1:])
        if isCancell: # 取り消し, 中止の馬がきたら次に行く。その馬の推定上がりを無視する。
            isCancell = False
            continue
        if zeroAgari:
            zeroAgari = False
            tmp.append(0)
        else:
            tmp.append(float(a)) # 推定上がりはfloat型
        if tmp[0] == 1:
            infos = info.pop(0)
            date = str(re.search(r'\d+:\d+', infos).group()) # 2数字:2数字を取得
            course = str(infos[6:7])
            meter = int(re.search(r'\d{4}', infos).group()) # 数字が4つ連続
            direction = str(re.findall(r'\((.+)\)', infos)[0]) # 括弧内に含まれる文字
            if infos[-2] != " ":
                weather = str(infos[-2:])
            else:
                weather = str(infos[-1])
            status = info.pop(0)
        tmp += date, course, meter, direction, weather, status
        merge.append(tmp)
    return pd.DataFrame(merge, index=None, columns=columns)


# テキストに保存したデータをリストにする方法
def readTextfiles():
    """テキストデータの読み込み

    テキストデータをlist型で読み込みをする。

        Returns:
            data(list):
                ``data.txt``のリスト
            agari(list):
                ``agari.txt``のリスト
            info(list):
                ``race_info.txt``のリスト

    """
    data = []
    agari = []
    with open("../data/scraping_datas/data.txt", "r") as s:
        data = s.read().splitlines()
    with open("../data/scraping_datas/agari.txt", "r") as a:
        agari = a.read().splitlines()
    with open("../data/scraping_datas/race_info.txt", "r") as i:
        info = i.read().splitlines()
    return data, agari, info

if __name__ == "__main__":
    data, agari, info = readTextfiles()
    csv = csv_generator(data, agari, info)
    csv.to_csv("../data/scraping_datas/all2019_2.csv", encoding="shift-jis")
