# netkeibaをscraping
from selenium import webdriver
from selenium.webdriver.common.by import By
import chromedriver_binary as driver
import time

class Netkeiba:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.race_list_url = [] # eventのURLの保持
        self.race_result_url = [] # raceのURLの保持
        self.horse_url = [] # 馬のURLの保持

    def setDriver(self, url):
        self.driver.get(url)

    def delDriver(self):
        self.driver.close()
        self.driver.quit()

    def getEventURL(self, year):
        """
        指定した年の12 ~ 1月までの東京で開催されたURLの取得。
        """
        for month in range(11,9,-1): # 12 ~ 1月まで
            elements = self.driver.find_elements_by_tag_name("a")
            for e in elements:
                url = e.get_attribute("href")
                try:
                    if "?pid=race_list&kaisai_id=201905" in url: # 一旦東京のレースのみ
                        self.race_list_url.append(url)
                except TypeError:
                    continue
            # 次の月を表示
            self.driver.execute_script("changeMonth( "+str(year)+", "+str(month)+" );")
            time.sleep(2) # ゆっくりアクセス
    
    def getRaceURL(self):
        """
        getEventURLで取得した競技のURLからレースごとのURLを取得する
        """
        #self.setDriver(self.race_list_url[0])
        for race_list in self.race_list_url:
            self.setDriver(race_list)
            elements = self.driver.find_elements_by_tag_name("a")
            for e in elements:
                url = e.get_attribute("href")
                try:
                    if "?pid=race_result&race_id" in url:
                        self.race_result_url.append(url)
                except TypeError:
                    continue
            time.sleep(2) # ゆっくりアクセス

    def getRaceResult(self):
        """
        getRaceURLに基づきレースの結果を取得する。
        またそのレースに出場している馬のURLはhorse_urlに保存される。ただしレースごとなので毎回初期化される。
        辞書型で馬が出場しているURLを保存させてもいいかも！！おいしいかも~
        """
        #self.setDriver(self.race_result_url[0])
        for race in self.race_result_url:
            self.setDriver(race)
            self.horse_url = [] # レースごとになのでここで初期化が必要。 それだとclass変数にしなくても良い感じかな
            self.driver.find_element_by_class_name("Button_01").click() # 非表示部分を表示させる。
            tables = self.driver.find_element_by_id("All_Result_Table")
            trs = tables.find_elements(By.TAG_NAME, "tr")
            hor = tables.find_elements(By.TAG_NAME, "a")
            for i in range(1,len(trs)):
                tds = trs[i].find_elements(By.TAG_NAME, "td")
                for j in range(0,len(tds)):
                    print(tds[j].text) # 馬ごとの様々な情報が表示される。
                self.horse_url.append(hor[i-1].get_attribute("href"))
                #print(hor[i-1].get_attribute("href")) # 馬のURL
            self.getHorseAgari(str(race.split("=")[2])) # lastDateはレースの日時

    def getHorseAgari(self, lastDate):
        """
        lastDateは推定上がりを取得したい馬が最後にレースした日時を上げる。
        基本的にレースが行われた日時を入れるだけ。
        形式は "201905050112"　こんな感じ。
        レースURLの最後を渡せばいい
        """
        #self.setDriver(self.horse_url[0])
        for uma in self.horse_url:
            self.setDriver(uma)
            horse = self.driver.find_element_by_tag_name("h2")
            old_race = self.driver.find_elements_by_tag_name("a")
            isBreak = False
            url = ""
            for old in old_race:
                try:
                    if("race/20" in old.get_attribute("href")): # レースのURLのみ
                        url = old.get_attribute("href")
                        if(isBreak): break # 前回の大会は、現在の大会の次にくる
                        if(url.split("/")[4] == lastDate): # 現在の大会が来たらBreakをTrueにする
                            isBreak = True
                except TypeError:
                    continue
            horse_name = horse.text # 推定上がりを取得したい馬の名前を保存
            # 推定上がりを取りにいく
            self.setDriver(url)
            tds = self.driver.find_elements(By.TAG_NAME, "td")
            for i in range(len(tds)):
                if(tds[i].text == horse_name):
                    print(tds[i+8].text) # 推定上がりは名前から+8番目
                    break

# テストするやつ。
def test():
    mae = "201905050112"
    url = "https://db.sp.netkeiba.com/horse/2015110103/"
    driver = webdriver.Chrome()
    driver.get(url)
    horse = driver.find_element_by_tag_name("h2")
    old_race = driver.find_elements_by_tag_name("a")
    isBreak = False
    for old in old_race:
        try:
            if("race/20" in old.get_attribute("href")):
                url = old.get_attribute("href")
                if(isBreak): break
                if(url.split("/")[4] == mae):
                    isBreak = True
        except TypeError:
            continue
    print(horse.text)
    name = horse.text
    # 推定上がりを取りにいく
    driver.get(url)
    tds = driver.find_elements(By.TAG_NAME, "td")
    for i in range(len(tds)):
        if(tds[i].text == name):
            print(tds[i+8].text) # 推定上がりは名前から+8番目
            break
    driver.close()
    driver.quit()


if __name__ == "__main__":
    #test()
    nk = Netkeiba()
    nk.setDriver("https://race.sp.netkeiba.com/?pid=race_calendar&rf=faq")
    nk.getEventURL("2019")
    nk.getRaceURL()
    nk.getRaceResult()
    nk.delDriver()