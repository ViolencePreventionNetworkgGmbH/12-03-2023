from cProfile import label
from csv import excel
from lib2to3.pgen2.driver import Driver
from attr import attrs
import mysql.connector
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import pandas as pd
from soupsieve import select
import datetime
import numpy as np
import math
#import matplotlib.pyplot as plt 

from dateutil.parser import parse
from fake_useragent import UserAgent
import logging
#to send emails
# import os
# import win32com.client as win32

#class crawler wo alle Funktionen für alle platformen existieren
class Crawler:
  #die Funktion beinhaltet die verbindung string mit Datenbank
  # user, password,host, database Name.
  def verbindung_mit_datenbank(self):
    #open connection to the database
    config = {'user': 'extern','password': 'Eec&Mv4WfgZ@bt','host': '85.214.197.248','database': 'am8423','raise_on_warnings': True}
    return config
  
  def daten_speichern(self):
    
    return False

  #die Funktion beinhaltet der Pfad zu Chrome driver
  def driver(self):
    #hier ist pfad wo chromedriver liegt / the path of chrome driver
    #wenn eine problem bei chrome gibt dann neue / passende chrome driver installieren und pfad hier aktualisieren
    chrome_pfad='C:/Users/AhmadAlsalman/Desktop/coding/chromedriver/chromedriver3.exe'

    return chrome_pfad
  #Funktion für Youtube crawler
  def youtube_crawler(self,verbindung_mit_datenbank,chrome_pfad,speichern):
    #die Erstellung von Logging um der verlauf zu dokumentieren
    logging.basicConfig(filename=f'C:/Users/AhmadAlsalman/OneDrive - Violence Prevention Network gGmbH/Desktop/Crawler/log/log_{datetime.date.today()}.log', level=logging.INFO)
    #chrome=chrome pfad in driver funktion
    #config=veerbindung information aus verbindung_mit_datenbank funktion
    speicher=speichern
    chrome=chrome_pfad
    config=verbindung_mit_datenbank()
    mydb = mysql.connector.connect(**config)
    cursor=mydb.cursor(buffered=True)
    #call the youtube channel id from youtube_user table
    cursor.execute(""" SELECT youtube_id FROM youtube_user where youtube_user.Description ='Aktiv' """)
    users = cursor.fetchall()
    mydb.commit()
    logging.info('die verbindung mit datenbank ist hergestellt ')
    #looping durch alle Users ID in youtube_user tabelle 
    for user in users:
      try:
        #youtube_id als string
        urls=user[0]
        print('urls',urls)
        #chrome optionen defenieren
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"profile.default_content_settings.cookies": 2})
        options.add_experimental_option("detach", True)
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("user-data-dir=C:\\Users\\\AhmadAlsalman\\AppData\\Local\\Google\\Chrome\\User Data")
        driver = webdriver.Chrome(chrome_options=options, executable_path=chrome) 
        #for the page
        #open the chromedriver to open pages
        driver.get(f'https://www.youtube.com/@Islamictutors/about')
        #driver.get(f'https://www.youtube.com/channel/{urls}/about')
        print("driver.title : ",driver.title)
        print("driver.current_url : ",driver.current_url)
        logging.info(f'die kanal ist : {driver.current_url}')
        time.sleep(5)
        #to scroll down in the page
        timeout = time.time() + 60*5
        while True:
          scroll_height = 2000
          document_height_before = driver.execute_script("return document.documentElement.scrollHeight")
          driver.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
          time.sleep(5)
          document_height_after = driver.execute_script("return document.documentElement.scrollHeight")
          if document_height_after == document_height_before or time.time()>timeout:
            break

            
        #parsing the webseite mit Beautifulsoup
        content=driver.page_source.encode('utf-8').strip()
        soup=BeautifulSoup(content,'html.parser')
        #suchen nach elemente um ifnormationen zu sammeln
        #elemente wie Beschreibung, Bilder, name, .. etc....
        divs_description=soup.find_all('div',id="description-container")
        div_bild=soup.find_all('yt-img-shadow',id="avatar")
        for item in divs_description:
          description_ = item.find('yt-formatted-string',{'class':'style-scope ytd-channel-about-metadata-renderer'}).text.strip()
          description=description_[:900]
          #print('description : ',description)
        print(div_bild)
        try:
          for item2 in div_bild:
            bild=(item2.find('img')['src'])
            print('vv:',bild)
            break
        except:
          bild='None'

        vid_list=[]
        chan_name_xp = '//*[@id="channel-name"]'
        chan_join = './/*[@id="right-column"]/yt-formatted-string[2]/span[2]'
        chan_views = './/*[@id="right-column"]/yt-formatted-string[3]'
        subs_xpath = '//*[@id="subscriber-count"]'
        videos_class = "style-scope ytd-grid-video-renderer"
        #kanal Name
        try:
          channel_name = driver.find_element(by=By.XPATH, value=chan_name_xp).text
          logging.info(f'die kanal name ist {channel_name}')
        except:
          logging.error('die kanal name koennte nicht gecrawlt')
          channel_name=""

        # Scrap Channel Join Date (about)
        try:
          channel_join = driver.find_element(by=By.XPATH, value=chan_join).text
          logging.info(f'kanal Datum ist : {chan_join}')
        except:
          logging.error('die veroeffentlichungsdatum ist nicht gecrawlt')
          channel_join=''

        # Scrap Channel Views (about)
        try:
          channel_views = driver.find_element(by=By.XPATH, value=chan_views).text
          views=(re.sub(" views", "", channel_views))
          views=int(re.sub(",", "", views))
          logging.info(f'kanal views : {views}')
        except:
          logging.error('views zahl könnte nicht gecrawlt')
          views=0
        # Scrap Channel subscribers (about)
        try:
          subscribers = driver.find_element(by=By.XPATH, value=subs_xpath).text
          #to reblace the letter M and K in susecribers number
          if "M" in subscribers:
            subscribers=(re.sub("M subscribers", "",subscribers))
            subscribers=float(subscribers)*1000000
            subscribers=int(subscribers)
          elif "K" in subscribers:
            subscribers=(re.sub("K subscribers", "",subscribers))
            subscribers=float(subscribers)*1000
            subscribers=int(subscribers)
          else:
            subscribers=int(0)
            logging.info(f'kanal subscribers : {subscribers}')
        except:
          logging.error('subscribers zahl könnte nicht gecrawlt')
          subscribers=int(0)

############################################ lives   #################################################################
        print('')
        print('')
        print('')
        print('')
        print('')
        time.sleep(2)
        #to click on live and count the number of videos
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/tp-yt-app-header-layout/div/tp-yt-app-header/div[2]/tp-yt-app-toolbar/div/div/tp-yt-paper-tabs/div/div/tp-yt-paper-tab[4]").click()
        time.sleep(5)
        timeout = time.time() + 60*5
        content=driver.page_source.encode('utf-8').strip()
        soup=BeautifulSoup(content,'html.parser')
        #scroll down
        while True:
          scroll_height = 2000
          document_height_before = driver.execute_script("return document.documentElement.scrollHeight")
          driver.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
          time.sleep(3)
          document_height_after = driver.execute_script("return document.documentElement.scrollHeight")
          if document_height_after == document_height_before or time.time()>timeout:
            break
        time.sleep(5)
        #parsing die webseite mit BeautifulSoup
        content=driver.page_source.encode('utf-8').strip()
        soup=BeautifulSoup(content,'html.parser')
        lives_list=[]
        lives=soup.find_all('a',id="thumbnail",href=True)
        #loop through all lives links/ videos
        for l in lives:
          
          link=l['href']
          #save all watch links/ videos in the list
          lives_list.append(f'https://www.youtube.com{link}')
        print("number of lives",len(lives_list))
        #loop through the list/ videos
        for live in lives_list:
          try:
            i=0
            logging.info('neues tab oeffnen ')
            #öffne der video in neues tab
            driver.switch_to.window(driver.window_handles[0])
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(live)
            time.sleep(5)
            
            print("driver2.current_url : ",driver.current_url)
            logging.info(f'video link is : {driver.current_url}')
            time.sleep(2)
            #to scroll down to get comment  info
            try:
              driver.execute_script(f"window.scrollTo(0,200);")
            except:
              print("scroling for comments didnt work")

            time.sleep(4)
            #parsing the page with beautifulsoup
            content2=driver.page_source.encode('utf-8').strip()
            soup2=BeautifulSoup(content2,'html.parser')
            #find all tags to relevent information 
            time.sleep(5)
            #likes
            try:
              likes_path=soup2.select('ytd-menu-renderer.ytd-watch-metadata > div:nth-child(1) > ytd-segmented-like-dislike-button-renderer:nth-child(1) > div:nth-child(1) > ytd-toggle-button-renderer:nth-child(1) > yt-button-shape:nth-child(1) > button:nth-child(1)')
              likes=likes_path[0].attrs['aria-label']
              likes=re.sub(',','',likes)
              likes=re.findall(r'\d+', likes)
              likes=int(likes[0])
              logging.info(f'likes : {likes}')
            except:
              logging.error('like zahl koennte nicht gecrawlt')
              likes=0
            #views
            try:
              views_path=soup2.select('tp-yt-paper-tooltip.ytd-watch-metadata > div:nth-child(1)')
              views=views_path[0].text
              views=(re.split('•',views))
              views=(re.sub(',','',views[0]))
              views=int(re.findall(r"[-+]?(?:\d*\.\d+|\d+)", views)[0])
              logging.info(f'views : {views}')
            except:
              logging.error('views zahl koennte nicht gecrawlt')
              views=0

            #publish_date
            #nicht alle videos haben die gleiche struktur, deshalb gibt es if und else
            try:
              date_path=soup2.select('tp-yt-paper-tooltip.ytd-watch-metadata > div:nth-child(1)')
              publish_date=views_path[0].text
              publish_date=(re.split('•',publish_date))
              publish_date=(re.sub(',','',publish_date[1]))

              publish_date=publish_date.replace('Streamed live on ','')
              publish_date=parse(publish_date)
              publish_date=publish_date.strftime('%Y-%m-%d')


              #publish_date=int(re.findall(r"[-+]?(?:\d*\.\d+|\d+)", publish_date)[0])
              print('publish date : ',publish_date)
              logging.info(f'Datum : {publish_date}')
            except:
              logging.error('Datum koennte nicht gecrawlt')
              publish_date="no date"

            #title
            try:
              title_path =soup2.select('h1.ytd-watch-metadata > yt-formatted-string:nth-child(1)')
              title=title_path[0].text
              logging.info(f'title : {title}')
            except:
              logging.error('title koennte nicht gecrawlt')
              title="no title"
            #description
            try:
              description_path =soup2.select('#bottom-row > div:nth-child(1)')
              description=description_path[0].text
              description=description[:490]
              logging.info(f'Beschreibung : {description}')
            except:
              logging.error('Beschreibung koennte nicht gecrawlt')
              description="no description"
            #comment
            try:
              comment_path = soup2.select('.count-text > span:nth-child(1)')
              comment=comment_path[0].text
              comment=(re.sub(',','',comment))
              logging.info(f'comments : {comment}')
            except:
              logging.error('comments koennte nicht gecrawlt')
              comment=0
            #duration
            try:
              duration_path=soup2.select('.ytp-time-duration')
              duration=duration_path[0].text
              print("duration : ",duration)
              logging.info(f'duration : {duration}')
            except:
              logging.error('duration koennte nicht gecrawlt')
              duration="no duration"

            try:
              keywords_selector=soup2.select('head > meta:nth-child(55)')
              keywords=keywords_selector[0].attrs['content']
              keywords=keywords[:190]
            except:
              keywords='None'

            
            print('channel',channel_name)
            print('urls',urls)
            print('video',live)
            print('title',title)
            print('keywords',keywords)
            print('description',description)
            print('publish_date',publish_date)
            print('views',views)
            print('likes',likes)
            print('comment',comment)
            print('duration',duration)
            print('Crawl_date',datetime.date.today())
            time.sleep(5)
            #get the user id from youtube_user to save the relational data for every user 
            if speicher==True:
              try:
                print('---------- saving --------------------------')
                cursor.execute(f""" SELECT ID FROM youtube_user WHERE youtube_id='{urls}' """)
                the_user = cursor.fetchone()
                mydb.commit()
                print("the user is : ", the_user[0])
                #insert the data to the table
                sql = "INSERT INTO youtube_youtube_posts (user_id_id, user_name , channel_id , Video_id , title  , post_Description, Publiched_At  , viewCount , likeCount  , favoriteCount , commentCount  , duration  ,Crawl_date, keywords ) VALUES (%s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s,%s, %s)"
                val = (int(the_user[0]), channel, urls, video, title, description, publish_date, views, likes, 0, comment, duration, datetime.date.today(),keywords)
                cursor.execute(sql, val)
                mydb.commit()
                print ("record inserted.",cursor.rowcount)
                logging.info(f'daten fuer : {driver.current_url} sind gespeichert')
              except:
                logging.error(f'daten fuer : {driver.current_url} koennte nicht gespeichert')
                print ("saving data for videos didnt work")
            #schließe den  driver und navegiere nach Main tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            logging.info('zurueck zu Main tab')
            #zählen nach jede videos damit der crawler nur die letzte 50 video crawlen
            
          except:
            logging.error(f' for loop durch : {live} nicht geklappt')
            print('the try through the for loop didnt work')

          i+=1
          if i ==1:
            break
         
              







        print('')
        print('')
        print('')
        print('')
##################################################  shorts   #######################################################

        print('shorts')
        print('shorts')
        print('shorts')
        print('shorts')
        print('shorts')
        time.sleep(2)
        #to click on shorts and count the number of videos
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/tp-yt-app-header-layout/div/tp-yt-app-header/div[2]/tp-yt-app-toolbar/div/div/tp-yt-paper-tabs/div/div/tp-yt-paper-tab[3]").click()
        time.sleep(5)
        timeout = time.time() + 60*5
        content=driver.page_source.encode('utf-8').strip()
        soup=BeautifulSoup(content,'html.parser')
        #scroll down
        while True:
          scroll_height = 2000
          document_height_before = driver.execute_script("return document.documentElement.scrollHeight")
          driver.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
          time.sleep(3)
          document_height_after = driver.execute_script("return document.documentElement.scrollHeight")
          if document_height_after == document_height_before or time.time()>timeout:
            break
        time.sleep(5)
        #parsing die webseite mit BeautifulSoup
        content=driver.page_source.encode('utf-8').strip()
        soup=BeautifulSoup(content,'html.parser')
        views_elements = soup.findAll(class_='inline-metadata-item style-scope ytd-video-meta-block')

        short_list=[]
        shorts=soup.find_all('a',id="thumbnail",href=True)
        #loop through all lives links/ videos
        for s in shorts:
          
          link=s['href']
          #save all short links/ videos in the list
          short_list.append(f'https://www.youtube.com{link}')
        print("number of shorts",len(short_list))
        #loop through the list/ videos
        index_views=0
        for short in short_list:
          try:
            logging.info('neues tab oeffnen ')
            #öffne der video in neues tab
            driver.switch_to.window(driver.window_handles[0])
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(short)
            time.sleep(5)
            
            print("driver2.current_url : ",driver.current_url)
            logging.info(f'video link is : {driver.current_url}')
            time.sleep(2)
            #to scroll down to get comment  info
            #parsing the page with beautifulsoup
            content2=driver.page_source.encode('utf-8').strip()
            soup2=BeautifulSoup(content2,'html.parser')
            #find all tags to relevent information 
            time.sleep(5)
            #views
            try:
                views_str = views_elements[index_views].text
                match = re.search(r'^([\d.]+)\s*([KM]?)\s*views?$', views_str)
                if match:
                    num, suffix = match.groups()
                    views = int(float(num) * (1000 if suffix == 'K' else 1000000 if suffix == 'M' else 1))
                    print(views)
                else:
                    print('Invalid view count format')
            except:
                logging.error('views zahl koennte nicht gecrawlt')
                views=0
            #likes
            try:
              likes_path=soup2.select('div:nth-child(3) > ytd-reel-player-overlay-renderer:nth-child(1) > div:nth-child(2) > div:nth-child(3) > ytd-like-button-renderer:nth-child(1) > ytd-toggle-button-renderer:nth-child(1) > yt-button-shape:nth-child(1) > label:nth-child(1) > div:nth-child(2) > span:nth-child(1)')
              likes=likes_path[0].text
              match = re.match(r'^(\d+(?:\.\d+)?)([KkMm])?$', likes)
              if match:
                  num = float(match.group(1))
                  mult = match.group(2)
                  if mult == 'K' or mult == 'k':
                      num *= 1000
                  elif mult == 'M' or mult == 'm':
                      num *= 1000000
                  likes = int(num)
              else:
                  print("Invalid input")
              logging.info(f'likes : {likes}')
            except:
              logging.error('like zahl koennte nicht gecrawlt')
              likes=0
            #title
            try:
              title_path =soup2.select('div:nth-child(3) > ytd-reel-player-overlay-renderer:nth-child(1) > div:nth-child(1) > ytd-reel-player-header-renderer:nth-child(1) > h2:nth-child(3) > yt-formatted-string:nth-child(1)')
              title=title_path[0].text
              logging.info(f'title : {title}')
            except:
              logging.error('title koennte nicht gecrawlt')
              title="no title"
            #comment
            try:
              comment_path = soup2.select('div:nth-child(3) > ytd-reel-player-overlay-renderer:nth-child(1) > div:nth-child(2) > div:nth-child(4) > ytd-button-renderer:nth-child(1) > yt-button-shape:nth-child(1) > label:nth-child(1) > div:nth-child(2) > span:nth-child(1)')
              comment=comment_path[0].text
              match = re.match(r'^(\d+(?:\.\d+)?)([KkMm])?$', comment)
              if match:
                  num = float(match.group(1))
                  mult = match.group(2)
                  if mult == 'K' or mult == 'k':
                      num *= 1000
                  elif mult == 'M' or mult == 'm':
                      num *= 1000000
                  comment = int(num)
              else:
                  print("Invalid input")
              logging.info(f'comments : {comment}')
            except:
              logging.error('comments koennte nicht gecrawlt')
              comment=0

            print('channel',channel_name)
            print('urls',urls)
            print('title',title)
            print('views',views)
            print('likes',likes)
            print('comment',comment)
            print('Crawl_date',datetime.date.today())
            time.sleep(5)
            #get the user id from youtube_user to save the relational data for every user 
            if speicher==True:
              try:
                print('---------- saving --------------------------')
                cursor.execute(f""" SELECT ID FROM youtube_user WHERE youtube_id='{urls}' """)
                the_user = cursor.fetchone()
                mydb.commit()
                print("the user is : ", the_user[0])
                #insert the data to the table
                sql = "INSERT INTO youtube_youtube_posts (user_id_id, user_name , channel_id , Video_id , title  , post_Description, Publiched_At  , viewCount , likeCount  , favoriteCount , commentCount  , duration  ,Crawl_date, keywords ) VALUES (%s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s,%s, %s)"
                val = (int(the_user[0]), channel, urls, video, title, description, publish_date, views, likes, 0, comment, duration, datetime.date.today(),keywords)
                cursor.execute(sql, val)
                mydb.commit()
                print ("record inserted.",cursor.rowcount)
                logging.info(f'daten fuer : {driver.current_url} sind gespeichert')
              except:
                logging.error(f'daten fuer : {driver.current_url} koennte nicht gespeichert')
                print ("saving data for videos didnt work")
            index_views+=1
            #schließe den  driver und navegiere nach Main tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            logging.info('zurueck zu Main tab')
            #zählen nach jede videos damit der crawler nur die letzte 50 video crawlen
            
          except:
            logging.error(f' for loop durch : {live} nicht geklappt')
            print('the try through the for loop didnt work')

          
          if index_views ==2:
            break
         
              







        print('')
        print('')
        print('')
        print('')

#############################################################################################################
        time.sleep(2)
        #to click on Home and count the number of videos
        driver.find_element(By.XPATH, "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/tp-yt-app-header-layout/div/tp-yt-app-header/div[2]/tp-yt-app-toolbar/div/div/tp-yt-paper-tabs/div/div/tp-yt-paper-tab[2]").click()
        time.sleep(5)
        timeout = time.time() + 60*5
        content=driver.page_source.encode('utf-8').strip()
        soup=BeautifulSoup(content,'html.parser')
        #scroll down
        while True:
          scroll_height = 2000
          document_height_before = driver.execute_script("return document.documentElement.scrollHeight")
          driver.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
          time.sleep(3)
          document_height_after = driver.execute_script("return document.documentElement.scrollHeight")
          if document_height_after == document_height_before or time.time()>timeout:
            break
        time.sleep(5)
        #parsing die webseite mit BeautifulSoup
        content=driver.page_source.encode('utf-8').strip()
        soup=BeautifulSoup(content,'html.parser')
        #nach elemente in Video tabs suchen
        divs_channel=soup.find_all('div',id="text-container")
        channel=" "
        for item6 in divs_channel:
          channel = item6.find('yt-formatted-string',{'class':'style-scope ytd-channel-name'}).text.strip()
          print('channel-name  : ',channel)
          break
        time.sleep(5)
        #methode 2 die zahl die videos aus youtube crawlen und nicht zählen
        try:
          videos2_path=soup.select('#videos-count > span:nth-child(1)')
          videos2_count=videos2_path[0].text
          print('videos2_count ::::::::::::::',videos2_count)
        except:
          print('method 2 for number of videos didnt work')

        watch_list=[]
        watch=soup.find_all('a',id="thumbnail",href=True)
        #loop through all watch links/ videos
        for w in watch:
          link=w['href']
          #save all watch links/ videos in the list
          watch_list.append(f'https://www.youtube.com{link}')

        print("number of videos",len(watch_list))
        number_of_videos=len(watch_list)
        logging.info(f'zahl die videos : {number_of_videos}')
        about_items = {
        "channel_name": channel_name,
        "channel_join_date": channel_join,
        "channel_views": channel_views,
        "views":views,
        "channel_description": description,
        "subscribers":subscribers,
        "Bild":bild,
        "number of videos":number_of_videos,
        }
        vid_list.append(about_items)
        print('vid_list',vid_list)

        if speicher==True:

          try:
            print('---------- saving --------------------------')
            #get User ID from youtube_user to save the relational data
            cursor.execute(f""" SELECT ID FROM youtube_user WHERE youtube_id='{urls}' """)
            the_user = cursor.fetchone()
            mydb.commit()
            print("the user is : ", the_user[0])
            #insert the data 
            sql = "INSERT INTO youtube_youtube_user (User_id_id, Channel_Name  , Channel_ID  , channel_Description , Publiched_At  , Subscriber_Count, View_Count  , Video_Count  , Playlist_Count , Link_photo  , Country  ,Crawl_date,uploads_id ) VALUES (%s,%s, %s,%s, %s,%s, %s,%s, %s,%s,%s, %s,%s)"
            val = (int(the_user[0]), channel_name, urls, description, channel_join, subscribers, views, number_of_videos, 0,  bild, 'none', datetime.date.today(), 'none')
            cursor.execute(sql, val)
            mydb.commit()
            print ("record inserted.",cursor.rowcount)
            logging.info(f'daten fuer kanal  {channel_name}  sind gespeichert ')
          except:
            logging.error(f'daten fuer kanal  {channel_name}  könnte nicht gespeichert')
            print ("saving data for the channel didnt work")

        time.sleep(5)


        logging.info('loop throogh the videos')
        i=0
        #loop through the list/ videos
        for video in watch_list:
          try:
            logging.info('neues tab oeffnen ')
            #öffne der video in neues tab
            driver.switch_to.window(driver.window_handles[0])
            driver.execute_script("window.open('');")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(video)
            time.sleep(5)
            
            print("driver2.current_url : ",driver.current_url)
            logging.info(f'video link is : {driver.current_url}')
            time.sleep(2)
            #to scroll down to get comment  info
            try:
              driver.execute_script(f"window.scrollTo(0,200);")
            except:
              print("scroling for comments didnt work")

            time.sleep(4)
            #parsing the page with beautifulsoup
            content2=driver.page_source.encode('utf-8').strip()
            soup2=BeautifulSoup(content2,'html.parser')
            #find all tags to relevent information 
            time.sleep(5)
            #likes
            try:
              likes_path=soup2.select('ytd-menu-renderer.ytd-watch-metadata > div:nth-child(1) > ytd-segmented-like-dislike-button-renderer:nth-child(1) > div:nth-child(1) > ytd-toggle-button-renderer:nth-child(1) > yt-button-shape:nth-child(1) > button:nth-child(1)')
              likes=likes_path[0].attrs['aria-label']
              likes=re.sub(',','',likes)
              likes=re.findall(r'\d+', likes)
              likes=int(likes[0])
              logging.info(f'likes : {likes}')
            except:
              logging.error('like zahl koennte nicht gecrawlt')
              likes=0
            #views
            try:
              views_path=soup2.select('html body ytd-app div#content.style-scope.ytd-app ytd-page-manager#page-manager.style-scope.ytd-app ytd-watch-flexy.style-scope.ytd-page-manager.hide-skeleton div#columns.style-scope.ytd-watch-flexy div#primary.style-scope.ytd-watch-flexy div#primary-inner.style-scope.ytd-watch-flexy div#below.style-scope.ytd-watch-flexy ytd-watch-metadata.watch-active-metadata.style-scope.ytd-watch-flexy div#above-the-fold.style-scope.ytd-watch-metadata div#bottom-row.style-scope.ytd-watch-metadata div#description.item.style-scope.ytd-watch-metadata div#description-inner.style-scope.ytd-watch-metadata tp-yt-paper-tooltip.style-scope.ytd-watch-metadata div#tooltip.style-scope.tp-yt-paper-tooltip.hidden')
              views=views_path[0].text
              views=(re.split('•',views))
              views=(re.sub(',','',views[0]))
              views=int(re.findall(r"[-+]?(?:\d*\.\d+|\d+)", views)[0])
              logging.info(f'views : {views}')
            except:
              logging.error('views zahl koennte nicht gecrawlt')
              views=0

            #publish_date
            #nicht alle videos haben die gleiche struktur, deshalb gibt es if und else
            try:
              publish_date_path =soup2.select('yt-formatted-string.ytd-video-primary-info-renderer:nth-child(2)')
              publish_date_text=publish_date_path[0].text
              if 'Premiered ' in publish_date_text:
                publish_date_text=publish_date_text.replace('Premiered ','')
                publish_date=parse(publish_date_text)
                publish_date=publish_date.strftime('%Y-%m-%d')
                print('publish date : ',publish_date)
              elif 'Streamed live on ' in publish_date_text:
                publish_date_text=publish_date_text.replace('Streamed live on ','')
                publish_date=parse(publish_date_text)
                publish_date=publish_date.strftime('%Y-%m-%d')
                print('publish date : ',publish_date)
              elif 'Premiered on ' in publish_date_text:
                publish_date_text=publish_date_text.replace('Premiered on ','')
                publish_date=parse(publish_date_text)
                publish_date=publish_date.strftime('%Y-%m-%d')
                print('publish date : ',publish_date)
              else:
                publish_date=parse(publish_date_text)
                publish_date=publish_date.strftime('%Y-%m-%d')
                print('publish date : ',publish_date)
                logging.info(f'Datum : {publish_date}')
            except:
              logging.error('Datum koennte nicht gecrawlt')
              publish_date="no date"

            #title
            try:
              title_path =soup2.select('h1.ytd-watch-metadata > yt-formatted-string:nth-child(1)')
              title=title_path[0].text
              logging.info(f'title : {title}')
            except:
              logging.error('title koennte nicht gecrawlt')
              title="no title"
            #description
            try:
              description_path =soup2.select('#bottom-row > div:nth-child(1)')
              description=description_path[0].text
              description=description[:490]
              logging.info(f'Beschreibung : {description}')
            except:
              logging.error('Beschreibung koennte nicht gecrawlt')
              description="no description"
            #comment
            try:
              comment_path = soup2.select('.count-text > span:nth-child(1)')
              comment=comment_path[0].text
              comment=(re.sub(',','',comment))
              logging.info(f'comments : {comment}')
            except:
              logging.error('comments koennte nicht gecrawlt')
              comment=0
            #duration
            try:
              duration_path=soup2.select('.ytp-time-duration')
              duration=duration_path[0].text
              print("duration : ",duration)
              logging.info(f'duration : {duration}')
            except:
              logging.error('duration koennte nicht gecrawlt')
              duration="no duration"

            try:
              keywords_selector=soup2.select('head > meta:nth-child(55)')
              keywords=keywords_selector[0].attrs['content']
              keywords=keywords[:190]
            except:
              keywords='None'

            
            print('channel',channel)
            print('urls',urls)
            print('video',video)
            print('title',title)
            print('keywords',keywords)
            print('description',description)
            print('publish_date',publish_date)
            print('views',views)
            print('likes',likes)
            print('comment',comment)
            print('duration',duration)
            print('Crawl_date',datetime.date.today())
            time.sleep(5)
            #get the user id from youtube_user to save the relational data for every user 
            if speicher==True:
              try:
                print('---------- saving --------------------------')
                cursor.execute(f""" SELECT ID FROM youtube_user WHERE youtube_id='{urls}' """)
                the_user = cursor.fetchone()
                mydb.commit()
                print("the user is : ", the_user[0])
                #insert the data to the table
                sql = "INSERT INTO youtube_youtube_posts (user_id_id, user_name , channel_id , Video_id , title  , post_Description, Publiched_At  , viewCount , likeCount  , favoriteCount , commentCount  , duration  ,Crawl_date, keywords ) VALUES (%s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s,%s, %s)"
                val = (int(the_user[0]), channel, urls, video, title, description, publish_date, views, likes, 0, comment, duration, datetime.date.today(),keywords)
                cursor.execute(sql, val)
                mydb.commit()
                print ("record inserted.",cursor.rowcount)
                logging.info(f'daten fuer : {driver.current_url} sind gespeichert')
              except:
                logging.error(f'daten fuer : {driver.current_url} koennte nicht gespeichert')
                print ("saving data for videos didnt work")
            #schließe den  driver und navegiere nach Main tab
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            logging.info('zurueck zu Main tab')
            #zählen nach jede videos damit der crawler nur die letzte 50 video crawlen
            i+=1
            if i ==50:
              break
          except:
            logging.error(f' for loop durch : {video} nicht geklappt')
            print('the try through the for loop didnt work')
            try:
              driver.close()
            except:
              logging.error('driver ist schon geschlossen')
              print("first driver already closed")

        try:
          driver.close()  
        except:
          print("iii")

      except:
        logging.error(f'try durch user : {user[0]} hat nicht geklappt') 
        print('the second  try for loop through channel didnt work')
        try:
          driver.close()
        except:
          logging.error('driver durch kanal / erste driver ist schon geschlossen')
          print("third driver already closed")

  #Funktion für Tiktok crawler
  def tiktok_crawler(self,verbindung_mit_datenbank, chrome_pfad,speichern):
    logging.basicConfig(filename=f'C:/Users/AhmadAlsalman/OneDrive - Violence Prevention Network gGmbH/Desktop/Crawler/log/log_{datetime.date.today()}.log', level=logging.INFO)
    speicher=speichern
    chrome=chrome_pfad
    #open connection to the database
    config=verbindung_mit_datenbank()
    mydb = mysql.connector.connect(**config)
    cursor=mydb.cursor(buffered=True)
    print('connection', mydb) 
    cursor=mydb.cursor(buffered=True)
    #call the tiktok channel id from tiktok_user table
    cursor.execute(""" SELECT tiktok_id FROM tiktok_user where tiktok_user.Description ='Aktiv' """)
    users = cursor.fetchall()
    mydb.commit()
    logging.info('die verbindung mit datenbank ist hergestellt ')
    
    
      #loop durch alle users
    for user in users:
      try:
        urls=user[0]
        #chrome optionen defenieren
        #open chromedriver for the page
        '''options = webdriver.ChromeOptions()
        ua = UserAgent()
        user_agent = ua.random
        print('user_agent',user_agent)
        options.add_argument("--user-data-dir=C:/Users/AhmadAlsalman/Desktop/coding/tiktok")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("Cache-Control=no-cache")
        options.add_argument('--no-sandbox')
        options.add_argument('--dns-prefetch-disable')
        options.add_argument('--disable-dev-shm-usage')
        options.add_extension("C:/Users/AhmadAlsalman/OneDrive - Violence Prevention Network gGmbH/Desktop/coding/tiktok/crx/crx.crx")
        options.add_argument("--disable-web-security")
        options.add_argument('--ignore-certificate-errors')
        options.page_load_strategy='none'
        options.add_argument('--ignore-certificate-errors-spki-list')
        options.add_argument('--ignore-ssl-errors')
        #options.add_argument(f'user-agent={user_agent}')
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        options.add_experimental_option('useAutomationExtension',False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        #options.add_argument(f'user-agent={user_agent}')
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option("detach", True)
        driver = webdriver.Chrome(chrome_options=options, executable_path=chrome)
        driver.implicitly_wait(5)
        #driver.get(f'{urls}') 
        driver.get(f'https://www.tiktok.com/@die_ukhti')
        time.sleep(4)
        print("driver.title : ",driver.title)
        print("driver.current_url : ",driver.current_url)'''

        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--disable-popup-blocking")
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        options.add_experimental_option('useAutomationExtension',False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36') # Set a user agent string to avoid detection
        options.add_argument("--disable-extensions") # Disable browser extensions
        options.add_argument("--disable-gpu") # Disable GPU hardware acceleration
        options.add_argument("--disable-infobars") # Disable the "Chrome is being controlled by automated software" infobar
        options.add_argument("--disable-notifications") # Disable desktop notifications
        options.add_argument("--disable-default-apps") # Disable default Chrome apps
        options.add_argument("--disable-background-timer-throttling") # Disable throttling of background timers
        options.add_argument("--disable-backgrounding-occluded-windows") # Disable backgrounding of occluded windows
        options.add_argument("--disable-breakpad") # Disable crash reporting
        options.add_argument("--disable-component-extensions-with-background-pages") # Disable component extensions with background pages
        options.add_argument("--disable-features=TranslateUI") # Disable the TranslateUI feature
        options.add_argument("--disable-hang-monitor") # Disable the hang monitor
        options.add_argument("--disable-ipc-flooding-protection") # Disable IPC flooding protection
        options.add_argument("--disable-renderer-backgrounding") # Disable renderer backgrounding
        options.add_argument("--disable-sync") # Disable syncing of browser data
        options.add_argument("--disable-web-resources") # Disable web resources
        options.add_argument("--enable-automation") # Enable automation
        options.add_argument("--log-level=3") # Set the log level to "warning"
        options.add_argument("--remote-debugging-port=0") # Disable remote debugging
        options.add_argument("--start-maximized") # Start the browser maximized
        options.add_argument("--test-type") # Set the test type
        options.add_argument("--use-mock-keychain") # Use a mock keychain for testing purposes
        options.add_argument("--disable-site-isolation-trials") # Disable site isolation trials
        driver = webdriver.Chrome(options=options, executable_path=chrome)
        driver.implicitly_wait(10) # Increase the implicit wait time to 10 seconds to allow for slower page loads
        driver.get(f'https://www.tiktok.com/@die_ukhti')
        print("driver.title : ",driver.title)
        print("driver.current_url : ",driver.current_url)



        logging.info(f'die kanal  ist {urls}')
        time.sleep(4)

        #to close the captcha 
        try:
          consent_button_xpath = "//*[@id='verify-bar-close']"
          consent= WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, consent_button_xpath)))
          consent= driver.find_element_by_xpath(consent_button_xpath)
          consent.click()
        except:
          print("close the captcha didnt work")
        timeout = time.time() + 60*5

        print("scroll down")
        #scroll down
        while True:
          scroll_height = 500
          document_height_before = driver.execute_script("return document.documentElement.scrollHeight")
          driver.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
          time.sleep(3)
          document_height_after = driver.execute_script("return document.documentElement.scrollHeight")
          if document_height_after == document_height_before or time.time()>timeout:
            break
        time.sleep(3)
        print("search for the data")
        #encode page to Beautifulsoup
        content=driver.page_source.encode('utf-8').strip()
        soup=BeautifulSoup(content,'html.parser')
        time.sleep(2)
        #search for the HTML tags and extract the data 
        #title and sub title
        try:
          title_path=soup.select('.tiktok-t89rw6-H2ShareTitle')
          title=title_path[0].text
          logging.info(f'title ist :  {title}')
        except:
          title='None'
          logging.error(f'title koennte nicht gecrawlt')

        try:
          subtitle_path=soup.select('.tiktok-qpyus6-H1ShareSubTitle')
          sub_title=subtitle_path[0].text
          logging.info(f'sub_title ist :  {sub_title}')
        except:
          sub_title='None'
          logging.error(f'sub_title koennte nicht gecrawlt')
        #bio
        try:
          bio_path=soup.select('.tiktok-1n8z9r7-H2ShareDesc.e1457k4r3')
          bio=bio_path[0].text
          logging.info(f'bio ist :  {bio}')
        except:
          logging.error(f'bio koennte nicht gecrawlt')
          bio='None'
        
        #following
        try:
          following=soup.find('strong',attrs={'data-e2e':'following-count'}).text
          if "M" in following:
            following=(re.sub("M", "",following))
            following=float(following)*1000000
            following=int(following)
          elif "K" in following:
            following=(re.sub("K", "",following))
            following=float(following)*1000
            following=int(following)
            logging.info(f'following ist : {following}')
        except:
          logging.error(f'following zahl koennte nicht gecrawlt')
          following=0
        #followers
        try:
          followers=soup.find('strong',attrs={'data-e2e':'followers-count'}).text
          if "M" in followers:
            followers=(re.sub("M", "",followers))
            followers=float(followers)*1000000
            followers=int(followers)
          elif "K" in followers:
            followers=(re.sub("K", "",followers))
            followers=float(followers)*1000
            followers=int(followers)
            logging.info(f'followers ist : {followers}')
        except:
          logging.error(f'followers zahl koennte nicht gecrawlt')
          followers=0
        #likes
        try:
          likes=soup.find('strong',attrs={'data-e2e':'likes-count'}).text
          if "M" in likes:
            likes=(re.sub("M", "",likes))
            likes=float(likes)*1000000
            likes=int(likes)
          elif "K" in likes:
            likes=(re.sub("K", "",likes))
            likes=float(likes)*1000
            likes=int(likes)
            logging.info(f'likes ist : {likes}')
        except:
          logging.error(f'likes zahl koennte nicht gecrawlt')
          likes=0
        #photo
        try:
          photo=''
          photo_=soup.select('#app > div.tiktok-ywuvyb-DivBodyContainer.e1irlpdw0 > div.tiktok-w4ewjk-DivShareLayoutV2.enm41490 > div > div.tiktok-1g04lal-DivShareLayoutHeader-StyledDivShareLayoutHeaderV2.enm41492 > div.tiktok-1gk89rh-DivShareInfo.ekmpd5l2 > div.tiktok-uha12h-DivContainer.e1vl87hj1 > span > img')
          photo=photo_[0].attrs['src']
        except:
          logging.error(f'photo  koennte nicht gecrawlt')
          photo=None
        #to search and save the videos links from the page and save it in the list
        links=[]
        div_video_container=soup.find_all("div",class_="tiktok-yz6ijl-DivWrapper e1cg0wnj1")
        video_links=[]
        for item in div_video_container:
          link=item.find('a')
          href=link['href']
          links.append(href)
        time.sleep(3)

        print('title : ',title)
        print('sub title : ',sub_title)
        print('following : ',following)
        print('followers : ',followers)
        print('likes-count : ',likes)
        print('number of videos : ',len(links))
        print('bio : ',bio)
        print('photo : ',photo)
        v=0
        if speicher==True:
          try:
            #get the user id from youtube_user to save the relational data for every user 
            cursor.execute(f""" SELECT ID FROM tiktok_user WHERE tiktok_id='{urls}' """)
            the_user = cursor.fetchone()
            mydb.commit()
            print("the user is : ", the_user[0])
            #insert the data to the table
            sql = "INSERT INTO tiktok_tiktok_channels (channel_id_id, Name , sub_title , channel_Description , followers  , following, like_Count  , video_Count , Link_photo  , Country , Crawl_date ) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s)"
            val = (int(the_user[0]), title, sub_title, bio, followers, following, likes, len(links),photo, 'None',datetime.date.today())
            cursor.execute(sql, val)
            mydb.commit()
            print ("record inserted.",cursor.rowcount)
            logging.info(f'daten fuer kanal  {urls}  sind gespeichert ')
          except:
            logging.error(f'daten für kanal  {urls}  koennte nicht gespeichert')
            print('saving the data for users didnt work')
        driver.execute_script("window.scrollTo(0, 150)")
        n=int(len(links))
        scrolling=200
        for i in range(1,30):
          try:
            driver.execute_script(f"window.scrollTo(0, {scrolling});")
            #to close the captcha
            try:
              consent_button_xpath = "//*[@id='verify-bar-close']"
              consent= WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, consent_button_xpath)))
              consent= driver.find_element_by_xpath(consent_button_xpath)
              consent.click()
            except:
              print("close the captcha didnt work")
            time.sleep(2)
            #encode page to Beautifulsoup
            content=driver.page_source.encode('utf-8').strip()
            soup=BeautifulSoup(content,'html.parser')
            #search for the HTML tags and extract the data 
            #views
            views_tag=f'.eegew6e2 > div > div:nth-child({i}) > div.tiktok-x6f6za-DivContainer-StyledDivContainerV2.eq741c50 > div > div > a > div > div.tiktok-11u47i-DivCardFooter.e148ts220 > strong'
            try:
              views = driver.find_element(by=By.CSS_SELECTOR, value=views_tag).text
              v_views=views
              if "M" in v_views:
                v_views=(re.sub("M", "",v_views))
                v_views=float(v_views)*1000000
                v_views=int(v_views)
              elif "K" in v_views:
                v_views=(re.sub("K", "",v_views))
                v_views=float(v_views)*1000
                v_views=int(v_views)
                logging.info(f'views : {v_views}')
            except:
              logging.error(f'view  koennte nicht gecrawlt')
              v_views=0
            #click on first post and open it in a new tab
            #after every post the number of i will increase 1 to fill the path automatically 

            try:
              first_post=f'.eegew6e2 > div > div:nth-child({i}) > div.tiktok-x6f6za-DivContainer-StyledDivContainerV2.eq741c50 > div > div > a'
              post = driver.find_element(by=By.CSS_SELECTOR, value=first_post).get_attribute('href')
              driver.execute_script("window.open('');")
              driver.switch_to.window(driver.window_handles[1])
              logging.info('neues tab oeffnen ')
              driver.get(post)
              logging.info(f'video link is : {driver.current_url}')
            except:
              print('Beiträge könnten nicht grfunden wurden')
              driver.close()
#####################################################################################
            try:
              # Find the video element
              video = driver.find_element_by_tag_name("video").click()
              video.send_keys(Keys.SPACE)
            except:
              print('vidio pause didnt work ')
              print('vidio pause didnt work ')
              print('vidio pause didnt work ')
            



            #closing captcha
            try:
              consent_button_xpath = "//*[@id='verify-bar-close']"
              consent= WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, consent_button_xpath)))
              consent= driver.find_element_by_xpath(consent_button_xpath)
              consent.click()
            except:
              print("close the captcha didnt work")
            time.sleep(5)
            driver.execute_script("window.scrollTo(0, 300)")
            time.sleep(5)
            soup2 = BeautifulSoup(driver.page_source,"html.parser")
            time.sleep(5)
            #to close the captcha
            try:
              consent_button_xpath = "//*[@id='verify-bar-close']"
              consent= WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, consent_button_xpath)))
              consent= driver.find_element_by_xpath(consent_button_xpath)
              consent.click()
            except:
              print("close the captcha didnt work")
###########################################################################
            #discription
            discription_path=soup2.select('.tiktok-1d7krfw-DivOverflowContainer.e1mzilcj5 > div')
            #'.tiktok-1fo8i23-DivContainer'
            try:
              discription=discription_path[0].text
              discription=discription[:490]
              logging.info(f'Beschreibung : {discription}')
            except:
              logging.error('Beschreibung koennte nicht gecrawlt')
              discription=None

            #music
            music_path='/html/body/div[2]/div[3]/div[2]/div[1]/div[2]/div[1]/div[1]/div[2]/h4/a'
            try:
              music=driver.find_element(by=By.XPATH, value=music_path).text
              logging.info(f'music : {music}')
            except:
              logging.error('music koennte nicht gecrawlt')
              music=None
            
            #likes
            #like_path=soup2.select('.tiktok-wxn977-StrongText.edu4zum2')
            like_path=soup2.select('.tiktok-79f36w-DivActionBarWrapper.eqrezik7 > div > button:nth-child(1) > strong')
            try:
              like=like_path[0].text
              print('like ::::: : ',like)
              if "M" in like:
                like=(re.sub("M", "",like))
                like=float(like)*1000000
                like=int(like)
              elif "K" in like:
                like=(re.sub("K", "",like))
                like=float(like)*1000
                like=int(like)
              elif "Like" in like:
                like=0
              logging.info(f'like : {like}')
            except:
              logging.error('like koennte nicht gecrawlt')
              like=0

            #comments
            try:
              comment_path=soup2.select('.tiktok-79f36w-DivActionBarWrapper.eqrezik7 > div > button:nth-child(2) > strong')
              comment=comment_path[0].text
              if "M" in comment:
                comment=(re.sub("M", "",comment))
                comment=float(comment)*1000000
                comment=int(comment)
              elif "K" in comment:
                comment=(re.sub("K", "",comment))
                comment=float(comment)*1000
                comment=int(comment)
              elif "Comment" in comment:
                comment=0

              logging.info(f'comments : {comment}')
            except:
              logging.error('comments koennte nicht gecrawlt')
              comment=0

            #share
            try:
              share_path=soup2.select('.tiktok-79f36w-DivActionBarWrapper.eqrezik7 > div > button:nth-child(3) > strong')
              share=share_path[0].text
              if "M" in share:
                share=(re.sub("M", "",share))
                share=float(share)*1000000
                share=int(share)
              elif "K" in share:
                share=(re.sub("K", "",share))
                share=float(share)*1000
                share=int(share)
              elif "Share" in share:
                share=0
              logging.info(f'share : {share}')
            except:
              logging.error('share koennte nicht gecrawlt')
              share=0

            #tags
            tags_path=soup2.select('.tiktok-1d7krfw-DivOverflowContainer.e1mzilcj5 > div')

            try:
              tags=tags_path[0].text
              tags=tags[:490]
              logging.info(f'tags : {tags}')
            except:
              logging.error('tags koennte nicht gecrawlt')
              tags=None

            #title
            title_path=soup2.select('.tiktok-1d7krfw-DivOverflowContainer.e1mzilcj5 > div')
            try:
              v_title=title_path[0].text
              v_title=title[:490]
              logging.info(f'v_title : {v_title}')
            except:
              logging.error('v_title koennte nicht gecrawlt')
              v_title=None


            #duration
            try:
              duration_path =  soup2.select('.tiktok-lh6ok5-SpanOtherInfos > span:nth-child(3)')
              duration=duration_path[0].text
              duration=re.findall(r'/([^\s/]+)', duration)[-1]
              logging.info(f'duration : {duration}')
            except:
              logging.error('duration koennte nicht gecrawlt')
              duration=None

            '''
            #publish date
            try:
              date_path = soup2.select('.tiktok-lh6ok5-SpanOtherInfos > span:nth-child(2)')
              published_at=date_path[0].text
              p=published_at.split()
              print('p : ', p)
              if  "ago" in p:
                s =p[0]
                print('s : ',s)
                parsed_s=re.findall(r'\d+',s)
                parsed_s=float(parsed_s[0])
                print('parsed_s : ',parsed_s)
                today = datetime.date.today()
                ddd = datetime.timedelta(days=parsed_s)
                past_time=today-ddd
                current_date=past_time.strftime('%Y-%m-%d')
                print('current_date', current_date)
              else:
                past_time=p[-1]
                print('past_time',past_time)
                new_time=parse(past_time)
                current_date=new_time.strftime('%Y-%m-%d')
                print('current_date2 ', current_date)
                logging.info(f'Datum : {current_date}')
            except:
              logging.error('Datum koennte nicht gecrawlt')
              current_date='No Date'
              '''

            try:
              date_path = soup2.select('.tiktok-sfaea2-SpanOtherInfos.e17fzhrb2 > span:nth-child(3)')
              published_at=date_path[0].text
              p=published_at.split()
              print('p : ', p)
              if "h" in published_at:
                current_date=datetime.date.today() 
              elif  "ago" in p:
                s =p[0]
                print('s : ',s)
                parsed_s=re.findall(r'\d+',s)
                parsed_s=float(parsed_s[0])
                print('parsed_s : ',parsed_s)
                today = datetime.date.today()
                ddd = datetime.timedelta(days=parsed_s)
                past_time=today-ddd
                current_date=past_time.strftime('%Y-%m-%d')
                print('current_date', current_date)
              
              else:
                past_time=p[-1]
                print('past_time',past_time)
                new_time=parse(past_time)
                current_date=new_time.strftime('%Y-%m-%d')
                print('current_date2 ', current_date)
                logging.info(f'Datum : {current_date}')
            except:
              logging.error('Datum koennte nicht gecrawlt')
              current_date='No Date' 
              

            print('title : ',title)
            print('discription : ',discription)
            print('music : ',music)
            print('like : ',like)
            print('comment : ',comment)
            print('share : ',share)
            print('tags : ',tags)
            print('published_at : ',current_date)
            print('duration : ', duration)
            print('views : ', v_views)

            time.sleep(4)
            if speicher==True:
              try:
                #get the user id from youtube_user to save the relational data for every user 
                print("the user is : ", the_user[0])
                #insert the data to the table
                sql = "INSERT INTO tiktok_tiktok_videos (channel_id_id, Name , Video_link , title , tags  , video_Description, viewCount  , likeCount , shareCount  , commentCount , duration  , Publiched_At  ,Crawl_date) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s,%s, %s)"
                val = (int(the_user[0]), title, driver.current_url, v_title, tags, discription, v_views, like, share, comment, duration,current_date, datetime.date.today())
                cursor.execute(sql, val)
                mydb.commit()
                print ("record inserted.",cursor.rowcount)
                logging.info(f'daten fuer : {driver.current_url} sind gespeichert')
                n+=1
              except:
                logging.error(f'daten fuer : {driver.current_url} koennte nicht gespeichert')
                print('saving the data for users didnt work')
            
            try:

              driver.close()
              scrolling+=30
              #going back to main tab
              driver.switch_to.window(driver.window_handles[0])
              logging.info('zurueck zu Main tab')
            except:
              logging.error(f'driver in 2451 ist schon geschlossen')
              print('driver already closed')

          except:
            logging.error(f' for loop durch  video nicht geklappt')
            print('the for loop throught videos didnt work')
            try:
              driver.switch_to.window(driver.window_handles[0])
            except:
              print('driver already switched ')

        try:
          driver.close()
        except:
          print('driver alrewady closed for users')

      except:
        print('loop throught users didnt work')
        try:
          driver.close()
        except:
          logging.error('driver already closed for users')
          print('driver already closed for users')
    
    try:
      driver.close()
    except:
      logging.error('driver 2491 ist schon geschlossen')
      print("driver at line 865 already closed")

  #Funktion für instagram crawler
  def Instagram_crawler(self,verbindung_mit_datenbank, chrome_pfad,speichern):
    logging.basicConfig(filename=f'C:/Users/AhmadAlsalman/Desktop/crawler methods/log_{datetime.date.today()}.log', level=logging.INFO)
    #open connection to the database
    speicher=speichern
    chrome=chrome_pfad
    config=verbindung_mit_datenbank()
    mydb = mysql.connector.connect(**config)
    cursor=mydb.cursor(buffered=True)
    #call the instagram_id  from instagram_user table
    cursor.execute(""" SELECT instagram_id FROM instagram_user where instagram_user.Description ='Aktiv' """)
    users = cursor.fetchall()
    mydb.commit()
    logging.info('die verbindung mit datenbank ist hergestellt ')
    
    try:
      #loop durch alle users
      for user in users:
        try:
          urls=user[0]
          #chrome optionen defenieren
          #open chromedriver for the page
          options = webdriver.ChromeOptions()
          ua = UserAgent()
          user_agent = ua.random
          print('user_agent',user_agent)
          #options.add_argument("--user-data-dir=C:/Users/AhmadAlsalman/Desktop/coding/tiktok")
          options.add_argument("--window-size=1920,900")
          options.add_argument("Cache-Control=no-cache")
          options.add_argument('--no-sandbox')
          options.add_argument('--dns-prefetch-disable')
          options.add_argument('--disable-dev-shm-usage')
          #options.add_extension("C:/Users/AhmadAlsalman/Desktop/coding/tiktok/crx/crx.crx")
          options.add_argument("--disable-web-security")
          options.add_argument('--ignore-certificate-errors')
          #options.page_load_strategy='none'
          options.add_argument('--ignore-certificate-errors-spki-list')
          options.add_argument('--ignore-ssl-errors')
          #options.add_argument(f'user-agent={user_agent}')
          options.add_experimental_option("excludeSwitches", ['enable-automation'])
          options.add_experimental_option('useAutomationExtension',False)
          options.add_argument('--disable-blink-features=AutomationControlled')
          #options.add_argument("--disable-popup-blocking")
          options.add_argument("user-data-dir=C:\\Users\\\AhmadAlsalman\\AppData\\Local\\Google\\Chrome\\User Data")
          options.add_experimental_option("detach", True)
          driver = webdriver.Chrome(chrome_options=options, executable_path=chrome)
          driver.implicitly_wait(5)
          #open chromedriver for the page
          driver.get(f'{urls}') 
          logging.info(f'die kanal  ist {urls}')
          logging.info(f'die title  ist {driver.title}')
          time.sleep(2)
          print("driver.title : ",driver.title)
          print("driver.current_url : ",driver.current_url)
          time.sleep(4)
          content=driver.page_source.encode('utf-8').strip()
          soup=BeautifulSoup(content,'html.parser')
          soup2 =BeautifulSoup(driver.page_source,"lxml")
          try:
            #login
            logging.info(f'Anmelden ...')
            time.sleep(5)
            username=driver.find_element_by_css_selector("input[name='username']")
            password=driver.find_element_by_css_selector("input[name='password']")
            username.clear()
            password.clear()
            username.send_keys("ahmad.alsalman@Violence-prevention-network.de")
            password.send_keys("Ah2022+Al##")
            login = driver.find_element_by_css_selector("button[type='submit']").click()
            #save your login info?
            time.sleep(10)
            notnow = driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
            #turn on notif
            time.sleep(10)
            notnow2 = driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
          except:
            logging.error(f'Anmeldung war unnoetig oder hat nicht geklappt')
            print('login didnt work')
          #the x-path for the elements on the user-page
          #channel_name
          try:
            channel_name_xp =soup2.select('h2.x1lliihq')
            channel_name=channel_name_xp[0].text
            logging.info(f'kanal name ist :  {channel_name}')
          except:
            logging.error(f'kanal name koennte nicht gecrawlt')
            channel_name=""
          #Verified ?
          try:
            Verified_xp=soup2.find('span', class_="_act0 _a9_u _9ys7") #.get_attribute("title")
            Verified=Verified_xp.text
            logging.info(f'Verification status ist :  {Verified}')
          except:
            logging.error(f'Verification koennte nicht gecrawlt')
            Verified='Not Verified'
          #posts
          try:
            posts_xp=soup2.findAll('span', class_="_ac2a")[0].text
            posts=posts_xp
            posts=re.sub(',','',posts)
            logging.info(f'posts zahl  ist :  {posts}')
          except:
            logging.error(f'posts zahl koennte nicht gecrawlt')
            posts=0
          #followers
          try:
            followers_xp=soup2.findAll('span', class_="_ac2a")[1]['title']
            followers=followers_xp
            followers=re.sub(',','',followers)
            logging.info(f'followers zahl  ist :  {followers}')
          except:
            logging.error(f'followers zahl koennte nicht gecrawlt')
            followers=""
          #following
          try:
            following_xp=soup2.findAll('span', class_="_ac2a")[2].text
            following =following_xp
            following=re.sub(',','',following)
            logging.info(f'following zahl  ist :  {following}')
          except:
            logging.error(f'following zahl koennte nicht gecrawlt')
            following=""
          #discription
          try:
            disc_head_xp=soup2.find('div', class_="_aa_c").text
            disc_head =disc_head_xp
            logging.info(f'kanal bio  ist :  {disc_head}')
          except:
            logging.error(f'kanal bio koennte nicht gecrawlt')
            disc_head=""

          
          Link_photo="n"
          time.sleep(5)
          print('channel_name : ',channel_name)
          print('Verified : ',Verified)
          print('posts : ',posts)
          print('followers : ',followers)
          print('following : ',following)
          print('disc_head : ',disc_head)
          if speicher==True:
            try:
              #get the user id from instagram_user to save the relational data for every user 
              cursor.execute(f""" SELECT ID FROM instagram_user WHERE instagram_id='{urls}' """)
              the_user = cursor.fetchone()
              mydb.commit()
              print("the user is : ", the_user[0])
              #insert the data to the table
              sql = "INSERT INTO instagram_instagram_channels (channel_id_id, Name , Verified , channel_Description , followers  , following, post_Count  , Link_photo   , Crawl_date ) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s)"
              val = (int(the_user[0]), channel_name, Verified, disc_head, followers, following, posts, Link_photo,datetime.date.today())
              cursor.execute(sql, val)
              mydb.commit()
              print ("record inserted.",cursor.rowcount)
              logging.info(f'daten fuer kanal  {urls}  sind gespeichert ')
            except:
              logging.error(f'daten für kanal  {urls}  koennte nicht gespeichert')
              print('saving the data for users didnt work')

          #to loop through the elements 
          time.sleep(10)
          try:
            #find and click on the first post
            try:
              first_post=driver.find_element_by_css_selector('div._ac7v:nth-child(1) > div:nth-child(1) > a:nth-child(1)').click()
              logging.info(f' click auf erste post ')
            except:
              logging.info(f' click auf erste post ')
            n=int(posts)
            i=0
            print('n  ::', n)
            #30 post crawlen
            for i in range(0,30):
              time.sleep(5)
              #parsing webseite
              soup2 =BeautifulSoup(driver.page_source,"lxml")
              logging.info(f'loop durch die Beiträge ')
              #title
              ##################################################################
              try:
                #title_path='/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/div[1]/ul/div/li/div/div/div[2]/div[1]/span'
                title_path=soup2.find('h1', class_="_aacl _aaco _aacu _aacx _aad7 _aade")
                title=title_path.text
                title=title[:490]
              except:
                title=''
              #likes
              try:
                #likes_path='/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div/div/a/div/span'
                likes_path=soup2.select('._aba- > div:nth-child(1) > a:nth-child(1) > div:nth-child(1)')
                #likes=driver.find_element(by=By.XPATH, value=likes_path).text
                likes=likes_path[0].text
                likes=re.sub(' likes','',likes)
                likes=re.sub(',','',likes)
                logging.info(f'likes : {likes}')
              except:
                logging.error(f'likes  koennte nicht gecrawlt')
                likes=None
              #Datum
              try:
                date_path=soup2.select('._aaqe')
                date=date_path[0].attrs['datetime']
                date=parse(date)
                date=date.strftime('%Y-%m-%d')
                logging.info(f'Datum : {date}')
              except:
                logging.error(f'Datum koennte nicht gecrawlt')
                date=None
              #bild
              try:
                img_path='/html/body/div[1]/div/div/div/div[1]/div/div/div/div[1]/section/main/div[1]/div[1]/article/div/div[1]/div/div[1]/div[2]/div/div/div/ul/li[2]/div/div/div/div/div[1]/img'
                img=driver.find_element(by=By.XPATH, value=img_path).get_attribute("src")
                logging.info(f'img : {img}')
              except:
                logging.error(f'img koennte nicht gecrawlt')
                img=None
              #views
              try:
                #views_path='/html/body/div[1]/div/div/div/div[2]/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/span/div/span'
                views_path=soup2.findAll('div', class_="_aacl _aaco _aacw _aacx _aad6 _aade")[1]
                views=views_path.text
                views=re.sub(' views','',views)
                views=re.sub(',','',views)
                logging.info(f'views : {views}')
              except:
                logging.error(f'views koennte nicht gecrawlt')
                views=None


              print('title :  ',title)
              print('likes :  ',likes)
              print('date :  ',date)
              print('img :  ',img)
              print('views : ',views)
              time.sleep(5)

            
              if speicher==True:
                try:
                  #get the instagram_id from instagram_user to save the relational data for every user 
                  cursor.execute(f""" SELECT ID FROM instagram_user WHERE instagram_id='{urls}' """)
                  the_user = cursor.fetchone()
                  mydb.commit()
                  print("the user is : ", the_user[0])
                  #insert the data to the table
                  sql = "INSERT INTO instagram_instagram_posts (channel_id_id, Name , post_link , title , viewCount  , likeCount, commentCount  , Publiched_At  , Crawl_date ) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s)"
                  val = (int(the_user[0]), channel_name,driver.current_url, title, views, likes, None, date,datetime.date.today())
                  cursor.execute(sql, val)
                  mydb.commit()
                  print ("record inserted.",cursor.rowcount)
                  logging.info(f'daten fuer   {driver.current_url}  sind gespeichert ')
                except:
                  logging.error(f'daten für   {driver.current_url}  koennte nicht gespeichert')
              #nach post crawlen , auf next clicken um nächte post zu crawlen
              next_butt='._aaqg > button:nth-child(1)'
              next_path=driver.find_element(by=By.CSS_SELECTOR, value=next_butt).click()
              time.sleep(5)
              logging.info(f'click auf Next Button ')

              
            try:
              driver.close()
            except:
              print('driver already closed')
                
          except:
            logging.error(f'daten für   {driver.current_url}  koennte nicht gespeichert')
            print('for loop through posts didnt work !')
            try:
              driver.close()
            except:
              print('driver already closed')

        except:
          print('loop through the users didnt work !')
        
        #ActionChains(driver).move_to_element(ll).perform() 
        
    except:
      logging.error(f'try durch user hat nicht geklappt') 
      print('loop through users didnt work ! ')


  #export die daten für tiktok als Excel
  def export_Tiktok_data_to_excel(self,verbindung_mit_datenbank):
    config=verbindung_mit_datenbank
    mydb = mysql.connector.connect(**config)
    df=pd.read_sql('select *  From tiktok_tiktok_videos  ORDER BY Name ',mydb)
    df.to_excel('C:/Users/AhmadAlsalman/OneDrive - Violence Prevention Network gGmbH/Desktop/Crawler/Tiktok/Excel/Tiktok_videos.xlsx')
    df2=pd.read_sql('select *  From  tiktok_tiktok_channels  ORDER BY Name ',mydb)
    df2.to_excel('C:/Users/AhmadAlsalman/OneDrive - Violence Prevention Network gGmbH/Desktop/Crawler/Tiktok/Excel/Tiktok_channels.xlsx')

  #export die daten für Youtube als Excel
  def export_Youtube_data_to_excel(self,verbindung_mit_datenbank):
    config=verbindung_mit_datenbank
    mydb = mysql.connector.connect(**config)
    df=pd.read_sql('select * From youtube_youtube_posts ORDER BY user_name ',mydb)
    df.to_excel('C:/Users/AhmadAlsalman/OneDrive - Violence Prevention Network gGmbH/Desktop/Crawler/Youtube/Excel/Youtube_videos.xlsx')
    df2=pd.read_sql('select * From youtube_youtube_user ORDER BY Channel_Name ',mydb)
    df2.to_excel('C:/Users/AhmadAlsalman/OneDrive - Violence Prevention Network gGmbH/Desktop/Crawler/Youtube/Excel/Youtube_channels.xlsx')
  #export die daten für instagram als Excel
  def export_instagram_data_to_excel(self,verbindung_mit_datenbank):
    config=verbindung_mit_datenbank
    mydb = mysql.connector.connect(**config)
    df=pd.read_sql('select *  From instagram_instagram_posts  ORDER BY Name ',mydb)
    df.to_excel('C:/Users/AhmadAlsalman/OneDrive - Violence Prevention Network gGmbH/Desktop/Crawler/Instagram/Excel/Instagram_posts.xlsx')
    df2=pd.read_sql('select *  From  instagram_instagram_channels  ORDER BY Name ',mydb)
    df2.to_excel('C:/Users/AhmadAlsalman/OneDrive - Violence Prevention Network gGmbH/Desktop/Crawler/Instagram/Excel/Instagram_channels.xlsx')

  # falls die verbindung mit datenbank nicht geschlossen ist , wird hier geschlossen
  def close_verbindung_mit_datenbank(self,verbindung_mit_datenbank):
    try:
      config=verbindung_mit_datenbank()
      mydb = mysql.connector.connect(**config)
      cursor=mydb.cursor(buffered=True)
      mydb.close()
    except:
      print('connection is already closed ')

  def send_email(self):
    # pip install pypiwin32 
    # construct Outlook application instance
    olApp = win32.Dispatch('Outlook.Application')
    olNS = olApp.GetNameSpace('MAPI')

    # construct the email item object
    mailItem = olApp.CreateItem(0)
    mailItem.Subject = 'Dummy Email'
    mailItem.BodyFormat = 1
    mailItem.Body = "Hello World"
    mailItem.To = '<Recipient Email>' 

    mailItem.Attachments.Add(os.path.join(os.getcwd(), 'bitcoin.png'))
    mailItem.Attachments.Add(os.path.join(os.getcwd(), 'csv file.png'))

    mailItem.Display()

    mailItem.Save()
    mailItem.Send()

#aufruf von class und die funktionen
crawler=Crawler()
crawler.youtube_crawler(crawler.verbindung_mit_datenbank,crawler.driver(),crawler.daten_speichern())
crawler.Instagram_crawler(crawler.verbindung_mit_datenbank,crawler.driver(),crawler.daten_speichern())
crawler.tiktok_crawler(crawler.verbindung_mit_datenbank,crawler.driver(),crawler.daten_speichern())
crawler.export_instagram_data_to_excel(crawler.verbindung_mit_datenbank())
crawler.export_Tiktok_data_to_excel(crawler.verbindung_mit_datenbank())
crawler.export_Youtube_data_to_excel(crawler.verbindung_mit_datenbank())
crawler.close_verbindung_mit_datenbank(crawler.verbindung_mit_datenbank())
