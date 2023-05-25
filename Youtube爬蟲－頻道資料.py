# -*- coding: utf-8 -*-
"""
Created on Sat May 29 17:47:01 2022
@author: Ivan
課程教材：行銷人轉職爬蟲王實戰｜5大社群平台＋2大電商
版權屬於「楊超霆」所有，若有疑問，可聯絡ivanyang0606@gmail.com
第六章 Youtube中尋找KOL夥伴
Youtube爬蟲－頻道資料

維修紀錄：
2023/5/4 因youtube網站調整，會導致抓不到影片的連結，因此重新修正了影片的ID標籤
2023/5/25 修復影片爬到none的問題，以及將滾動頁面改成動態偵測是否到底部的方式
"""
# selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime

# 自動下載ChromeDriver
service = ChromeService(executable_path=ChromeDriverManager().install())

# 關閉通知提醒
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)

# 開啟瀏覽器
driver = webdriver.Chrome(service=service, chrome_options=chrome_options)
time.sleep(5)

# 想爬取的youtube
youtuber = ['@TheKellyYang'
            ]

#準備容器
name = []
pageurl = []
intotime = []
looking = []
subscription = []
description = []
location = []
otherlink = []
channels = []
videolink = []
# 開始一個一個爬蟲
for yChannel in youtuber:

    #--- 簡介 部分
    driver.get('https://www.youtube.com/' + str(yChannel) + '/about')
    time.sleep(10)

    # 基本資料
    name.append(driver.find_element(by=By.ID, value='text-container').text) # 存youtuber頻道名
    pageurl.append('https://www.youtube.com/' + str(yChannel)) # 存頻道網址

    # 訂閱數輛
    getSubscription = driver.find_element(by=By.ID, value='subscriber-count').text
    getSubscription = getSubscription.replace(' 位訂閱者','')
    subscription.append(getSubscription)

    # 開始經營時間
    gettime = driver.find_element(by=By.XPATH, value='//div[@id="right-column"]/yt-formatted-string[2]/span[2]').text
    intotime.append(datetime.strptime(gettime, "%Y年%m月%d日"))

    # 總觀看次數
    getlooking = driver.find_element(by=By.XPATH, value='//div[@id="right-column"]/yt-formatted-string[3]').text
    getlooking = getlooking.replace('getlooking = ','')
    getlooking = getlooking.replace('觀看次數：','')
    getlooking = getlooking.replace('次','')
    getlooking = getlooking.replace(',','')
    looking.append(int(getlooking))

    # 2023/5/4 發現description這個ID標籤抓下來竟然不只一個...重新指定了正確的資料位置
    description.append(driver.find_elements(by=By.ID, value='description')[1].text) # 存文案

    location.append(driver.find_element(by=By.XPATH, value='//div[@id="details-container"]/table/tbody/tr[2]/td[2]').text) # 存國家位置

    # 其他連結
    getOtherlink = driver.find_elements(by=By.XPATH, value='//div[@id="link-list-container"]/a')
    containar = {} # 結果整理成dict
    for link in getOtherlink:
        containar[link.text] = link.get_attribute('href')
    otherlink.append(containar)

    #--- 頻道 部分
    driver.get('https://www.youtube.com/' + str(yChannel) + '/channels')
    time.sleep(10)

    getlink =  driver.find_elements(by=By.ID, value='channel-info')
    containar = {} # 結果整理成dict
    for link in getlink:
        data = link.text
        data = data.split('\n')
        # 檢查有沒有訂閱者
        if len(data) == 1:
            containar[data[0]] = {
                '訂閱數量':0,
                '連結':link.get_attribute('href')
                }
        else:
            containar[data[0]] = {
                '訂閱數量':data[1].replace(' 位訂閱者',''),
                '連結':link.get_attribute('href')
                }
    channels.append(containar)

    #--- 影片 部分
    driver.get('https://www.youtube.com/' + str(yChannel) + '/videos')
    time.sleep(10)

    # 滾動頁面
    # 2023/5/25 有些youtuber的影片非常多，因此滾動頁面的次數不能寫死，改以動態方式確保滾到最下面
    doit = True
    counter = len(driver.find_elements(by=By.ID, value='video-title-link'))
    while doit:
        driver.execute_script('window.scrollBy(0,5000)')
        time.sleep(5)
        # 判斷是否滾到底了
        if counter < len(driver.find_elements(by=By.ID, value='video-title-link')):
            counter = len(driver.find_elements(by=By.ID, value='video-title-link'))
        else:
            doit = False
            print('已經到頁面最底部')


    containar = [] # 結果整理成list
    # 2023/5/4 因youtube網站調整，會導致抓不到影片的連結，因此重新修正了影片的ID標籤
    for link in driver.find_elements(by=By.ID, value='video-title-link'):
        # 2023/5/25 影片最後會爬到None，須排除否則會造成下個爬取影片內容的步驟出錯
        if link.get_attribute('href') != None:
            containar.append(link.get_attribute('href'))
    videolink.append(containar)

dic = {
       'Youtuber頻道名稱' : name,
        '頻道網址' : pageurl,
        '開始經營時間' : intotime,
        '總觀看數' : looking,
        '總訂閱數' : subscription,
        '文案' : description,
        '國家位置' : location,
        '其他連結' : otherlink,
        '頻道' : channels,
        '所有影片連結' : videolink
       }
pd.DataFrame(dic).to_csv('Youtuber_頻道資料.csv',
                         encoding = 'utf-8-sig',
                         index=False)
