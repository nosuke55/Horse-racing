# netkeibaをscraping
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import chromedriver_binary as driver
import time

class Netkeiba:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(chrome_options=self.options) # headlessでの動作
        #self.driver = webdriver.Chrome()
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
        for month in range(12,1,-1): # 12 ~ 1月まで
            elements = self.driver.find_elements_by_tag_name("a")
            for e in elements:
                url = e.get_attribute("href")
                try:
                    if "?pid=race_list&kaisai_id=" in url: # 一旦東京のレースのみ
                        #print(url)
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
            try:
                self.driver.find_element_by_class_name("Button_01").click() # 非表示部分を表示させる。
            except Exception:
                print(race)
                time.sleep(2)
                continue
            tables = self.driver.find_element_by_id("All_Result_Table")
            trs = tables.find_elements(By.TAG_NAME, "tr")
            hor = tables.find_elements(By.TAG_NAME, "a")
            for i in range(1,len(trs)):
                tds = trs[i].find_elements(By.TAG_NAME, "td")
                for j in range(0,len(tds)):
                    with open("../data/scraping_datas/data.txt", "a") as f:
                        f.write(tds[j].text+"\n")
                    print(tds[j].text) # 馬ごとの様々な情報が表示される。
                self.horse_url.append(hor[i-1].get_attribute("href"))
                #print(hor[i-1].get_attribute("href")) # 馬のURL
            self.getHorseAgari(str(race.split("=")[2])) # lastDateはレースの日時
            time.sleep(2) # ゆっくりアクセス

    def getHorseAgari(self, lastDate):
        """
        lastDateは推定上がりを取得したい馬が最後にレースした日時を上げる。
        基本的にレースが行われた日時を入れるだけ。
        形式は "201905050112"　こんな感じ。
        レースURLの最後を渡せばいい
        """
        #self.setDriver(self.horse_url[0])
        for uma in self.horse_url:
            try:
                self.setDriver(uma)
            except Exception: # time out
                print("timeOutException: url is ", uma)
                with open("../data/scraping_datas/agari.txt", "a") as f:
                    f.write("0\n")
                time.sleep(2)
                continue
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
            try:
                self.setDriver(url)
            except Exception: # selenium.common.exceptions.InvalidArgumentException 初出場の馬は前回の大会のデータがないため。
                with open("../data/scraping_datas/agari.txt", "a") as f:
                    f.write("0\n") # 初出場の馬の推定上がりは0にする。make_cscの判定用。
                time.sleep(2)
                continue
            tds = self.driver.find_elements(By.TAG_NAME, "td")
            for i in range(len(tds)):
                if(tds[i].text == horse_name):
                    with open("../data/scraping_datas/agari.txt", "a") as f:
                        f.write(tds[i+8].text+"\n")
                    print(tds[i+8].text) # 推定上がりは名前から+8番目
                    break
            time.sleep(2) # ゆっくりアクセス


if __name__ == "__main__":
    nk = Netkeiba()
    #nk.setDriver("https://race.sp.netkeiba.com/?pid=race_calendar&rf=faq")
    #nk.getEventURL("2019")
    #nk.getRaceURL()
    #with open("race_urls.txt", "a") as f:
    #    for url in nk.race_result_url:
    #        f.write(str(url)+"\n")
    with open("race_urls2.txt", "r") as f:
        urls = f.read().splitlines()
    nk.race_result_url = urls
    nk.getRaceResult()
    nk.delDriver()
