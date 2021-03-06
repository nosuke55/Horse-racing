from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_binary as driver
import time
import csv
import pandas as pd
import sys
import os
import re
from selenium.common.exceptions import NoSuchElementException


#driver = webdriver.Chrome("/Users/higashikaito/selenium/chromedriver")
class Netkeiba:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.date_list_url = [] # eventの日付のURLの保持
        self.race_list_url = []  # eventのURLの保持
        self.race_result_url = []  # raceのURLの保持
        self.horse_url = []  # 馬のURLの保持

    def setDriver(self, url):
        self.driver.get(url)

    def classClick(self, class_name):
        self.driver.find_element_by_class_name(class_name).click()

    def delDriver(self):
        self.driver.close()
        self.driver.quit()
    #ページを開くための関数
    def getEventURL(self, event_url):
        list_add = []
        #self.driver.find_element_by_class_name("Button_01").click() # 非表示部分を表示させる。
        elements = self.driver.find_elements_by_tag_name("a")
        for e in elements:
            url = e.get_attribute("href")
            try:
                if event_url in url:#"/?pid=race_list&id=p" in url:  # 一旦東京のレースのみ
                    list_add.append(url)
            except TypeError:
                continue
        time.sleep(2)  # ゆっくりアクセス
        return list_add
    #HTML上のデータを持ってくる関数


    def getData(self, url):
        tables = self.driver.find_element_by_class_name("Shutuba_Table")  # _table_old nk_tb_common
        class_of_HorseList = self.driver.find_elements_by_class_name("HorseList")  #レースに出場する馬の数
        number_of_horse = len(class_of_HorseList)
        trs = tables.find_elements(By.TAG_NAME, "tr")
        hor = tables.find_elements(By.TAG_NAME, "a")
        ho_da2 = []  # dataの2次元配列
        for i in range(1, len(trs)):
            tds = trs[i].find_elements(By.TAG_NAME, "td")
            ho_da = []
            print(len(tds))
            for j in range(0, len(tds)):
                horse_info = tds[j].text
                if "--" in horse_info:
                    continue
                if "消" in horse_info:
                    continue
                if "牡" in horse_info or "牝" in horse_info:  # 性別, 年齢, 体重, 増減に分ける。
                    ho_da += horse_info[0], int(horse_info[1])
                    continue
                if "セ" in horse_info:  # せんばのための処理
                    try:
                        ho_da += horse_info[0], int(horse_info[1])
                        continue
                    except ValueError:
                        pass
                try:  # 体重と増減の処理
                    wei_sp = re.split('[()]', horse_info)
                    ho_da += int(wei_sp[0]), int(wei_sp[1])
                    continue
                except (ValueError, IndexError):
                    pass
                if len(ho_da) >= 11:
                    if "" == horse_info or " " == horse_info:
                        continue
                ho_da.append(tds[j].text)
                print(ho_da)
            if 0 == len(ho_da):
                continue
            ho_da2.append(ho_da)
            print(ho_da2)
        #columns = ["Ranking", "Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Horse_Weight", "Weight_Gain_or_Loss", "Trainer", "Jockey","Burden_Weight", "Winning_Popularity", "Estimated_Climb"]
        df = pd.DataFrame(ho_da2, columns=["Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Burden_Weight",
                                           "Jockey", "Trainer", "Horse_Weight", "odds", "Winning_Popularity"])  # TrainerとJockeyが逆、負担重量も場所が違う
        print(df)
        df.to_csv('df.csv', index=False)
        return df,number_of_horse

            
            
               
                #with open("../data/scraping_datas/data1.txt", "a") as f:
                    #f.write(tds[j].text+"\n")
                    #print(wow.text) # 馬ごとの様々な情報が表示される。
                #self.horse_url.append(hor[i-1].get_attribute("href"))
                #print(hor[i-1].get_attribute("href")) # 馬のURL
                
    def getEstimatedClimb(self,number_of_hose):#推定上がり
        horse_url=[]
        horse_url=nk.getEventURL("https://db.netkeiba.com/horse/")#馬のurlを取得
        est_cli = []
        #print(horse_url)
        for i in range(number_of_horse):#馬のデータのurl
            self.setDriver(horse_url[i])#レースのurlを開く
            try:
                tables = self.driver.find_element_by_class_name("nk_tb_common")
            except NoSuchElementException:
                est_cli.append(0)
                #print(est_cli)
                continue
            trs = tables.find_elements(By.TAG_NAME, "tr")#trがtableの中の１行に相当する
            for j in range(1,2):#一番最近のレースのurl
                tds = trs[j].find_elements(By.TAG_NAME, "td")
                for l in range(22,23):#上がりの列の箇所
                    try:
                        est_cli.append(float(tds[l].text))#推定上がりを取得
                        #print(tds[l].text)
                    except (NoSuchElementException,ValueError):
                        est_cli.append(float(0))
                        
                        #est_cli.append(0)
        df = pd.DataFrame(est_cli,columns = ["Estimated_Climb"])
        #print("pandas",df)
        return df

    def make_csv(self, df, df_ec):
        df_re = pd.concat([df, df_ec], axis=1)
        df_re = df_re[["Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Horse_Weight",
                       "Jockey", "Trainer", "Burden_Weight", "Winning_Popularity", "Estimated_Climb"]]
        df_re["Ranking"] = df_re["Horse_Num"]
        df_re = df_re[["Ranking", "Frame", "Horse_Num", "Horse_Name", "Sex", "Age", "Horse_Weight",
                       "Jockey", "Trainer", "Burden_Weight", "Winning_Popularity", "Estimated_Climb"]]
        #df_re.to_csv('../data/scraping_datas/df_1.csv', index=False )
        return df_re
        
    def save_csv(self, df, csv_title):
        df.to_csv('../data/' + csv_title + '.csv', index=False)


if __name__ == "__main__":
    nk = Netkeiba()
    nk.setDriver("https://racev3.netkeiba.com/top/")  # 最初のURL
    date_list_url = nk.getEventURL("race_list_sub.html?kaisai_date=")
    print("data_list_url =")
    print(date_list_url)
    race_list_url = []
    for i in date_list_url:
        nk.setDriver(i)#開催予定の日付のurlを開く
        race_list_url.append(list(dict.fromkeys(nk.getEventURL("netkeiba.com/race/shutuba.html"))))  # レースのurl
    print("race_rist_url = ")
    print(race_list_url)
    print(len(race_list_url[3]))

    for i, date_url in enumerate(race_list_url,):
        day = date_list_url[i][63:71]
        print(day)
        for j , race_url in enumerate(date_url,1):
            csv_title = str(day) + '_R' + str(j)
            print("最初のurl",race_url)
            nk.setDriver(race_url)  # レースのurlを開く
            df,number_of_horse = nk.getData(race_url)
            df_ec = nk.getEstimatedClimb(number_of_horse)
            df_re = nk.make_csv(df, df_ec)
            nk.save_csv(df_re, csv_title)

    nk.delDriver()
