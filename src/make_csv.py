import pandas as pd
import re

def csv_generator(data, agari):
    columns = ["Ranking", "Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Horse_Weight", "Weight_Gain_or_Loss", "Trainer", "Jockey",
                "Burden_Weight", "Winning_Popularity", "Estimated_Climb"]
    merge = []
    for a in agari:
        tmp = []
        while data != []:
            tmp_a = data.pop(0)
            if tmp_a == "着": continue # 着は無視!!
            if "牡" in tmp_a or "牝" in tmp_a or "せん" in tmp_a: # 性別, 年齢, 体重, 増減に分ける。
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
                tmp.append(tmp_a) # 名前はstring型
        tmp.append(float(a)) # 推定上がりはfloat型
        merge.append(tmp)
    return pd.DataFrame(merge, index=None, columns=columns)

# テキストに保存したデータをリストにする方法
def readTextfiles():
    data = []
    agari = []
    with open("../data/scraping_datas/test_data.txt", "r") as s:
        data = s.read().splitlines()
    with open("../data/scraping_datas/test_agari.txt", "r") as a:
        agari = a.read().splitlines()
    return data, agari

if __name__ == "__main__":
    data, agari = readTextfiles()
    csv = csv_generator(data, agari)
    print(csv)