from selenium import webdriver
from bs4 import BeautifulSoup
import json
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pandas as pd
import pymysql
from datetime import datetime
import boto3
import os
from urllib.request import urlopen
import uuid

driver = webdriver.Chrome("C:/Users/eunseo/AppData/Local/Temp/BNZ.633853164ec41f/chromedriver.exe")
regions = ['경기도', '경상북도', '경상남도', '서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시', '세종특별자치시', '강원도', '충청북도', '충청남도', '전라북도', '전라남도', '제주특별자치도']

driver.get('https://korean.visitkorea.or.kr/list/ms_list.do?choiceTag=%EC%97%AC%ED%96%89%EC%A7%80&choiceTagId=')
# driver.get('https://korean.visitkorea.or.kr/detail/ms_detail.do?cotid=9d506d09-62ec-40d4-87a2-a0fd35b25b80&big_category=A02&mid_category=A0201&big_area=35'
name = []
region = []
content = []
imagelist = []
address = []
lat=[]
lon=[]
images = []

for k in range(6, 9):
    print(k)
    v = "//*[@id='" + str(k) + "']"
    myInputElm = driver.find_element(by=By.XPATH, value=v)
    myInputElm.click()
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    print(soup)
    for ttmp in range(1, 2):
        va = "//*[@id='contents']/div[2]/div[1]/ul/li["+str(1)+"]/div[2]/div/a"
        driver.find_element(by=By.XPATH, value=va).send_keys(Keys.ENTER) #xpath값 클릭하기
        time.sleep(2)
        html = driver.page_source ## 페이지의 elements모두 가져오기
        soup = BeautifulSoup(html, 'html.parser') ## BeautifulSoup사용하기

        elements = soup.select('h2#topTitle')
        elements.extend((soup.select('div.area_address')))
        elements.extend((soup.select('div.inr>p')))


        travel = []

        for j in elements:
            travel.append(j.text)

        image = soup.find("img", class_="swiper-lazy swiper-lazy-loaded").get('src')
        images.append(image)
        # images = []
        # for j in range(len(image)):
        #     image = soup.find("img", class_="swiper-lazy swiper-lazy-loaded")
        #     images.append(image.get('src'))
        

        add = soup.select('div.inr>ul>li>span')
        for j in add:
            tmp = j.text.split(' ')
            if tmp[0] in regions:
                travel.append(j.text)

        time.sleep(2)
        # print(tmp)
        print("ss", travel)
        api_key = 'b821e0860b165d2a52fe06d433d69e03'

        def addr_to_lat_lon(addr):
            url = 'https://dapi.kakao.com/v2/local/search/address.json?query={address}'.format(address=addr)
            headers = {"Authorization": "KakaoAK " + api_key}
            result = json.loads(str(requests.get(url, headers=headers).text))
            match_first = result['documents'][0]['address']
            return float(match_first['x']), float(match_first['y'])


        search = travel[-1]
        print(search)
        try:
            d = addr_to_lat_lon(search)
            lon.append(d[0])
            lat.append(d[1])
        except:
            lon.append('')
            lat.append('')
        for j in travel:
            print(j)
        name.append(travel[0])
        region.append(travel[1].split(' ')[0])
        content.append(travel[2])
        address.append(travel[3])

        driver.execute_script("window.history.go(-1)")
        driver.refresh()
data = pd.DataFrame(zip(name, region, content, address,lat, lon), columns=['name', 'location', 'info', 'address', 'latitude', 'longitude'])

data.to_csv('C:/Users/eunseo/Desktop/study/여행지 지도.csv', index=False, encoding='cp949')
#
# # url = 'https://search.naver.com/search.naver?where=post&sm=tab_jum&query='+search
# # driver.get(url)
# # html = driver.page_source ## 페이지의 elements모두 가져오기
# # soup = BeautifulSoup(html, 'html.parser') ## BeautifulSoup사용하기
# #
# # elements = soup.select('._2yqUQ')
# # # print(soup)
# # arr = []
# # for i in elements:
# #     arr.append(i.text)
# #
# # print(arr)
#
# driver.close()


def s3_connection():
    try:
        # s3 클라이언트 생성
        s3 = boto3.client(
            service_name="s3",
            region_name="ap-northeast-2",
            aws_access_key_id="{아이디}",
            aws_secret_access_key="{비번}",
        )
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!") 
        return s3

def saveImageToS3(travelImg):
    s3 = s3_connection()
    travelImgInS3 = []
    for imageUrl in travelImg:
        imageTitle = "{}.jpg".format(uuid.uuid1())
        imageLocation = "travel_image/{}".format(imageTitle)
        with urlopen(imageUrl) as f:
            with open(imageLocation, 'wb') as h:
                img = f.read()
                h.write(img)
        s3.upload_file(imageLocation, "nadri-image", imageTitle)
        if os.path.exists(imageLocation):
            os.remove(imageLocation)
        s3Url = "https://nadri-image.s3.ap-northeast-2.amazonaws.com/{}".format(imageTitle)
        travelImgInS3.append(s3Url)
    return travelImgInS3


# DB 저장 
travelImgInS3 = saveImageToS3(images)
awsHost = "13.124.150.86"
loclaHost = "127.0.0.1"
conn = pymysql.connect(host=awsHost, user='ec2-user', password='root', db='nadri_gil', charset='utf8');

cur = conn.cursor();
id=0
for i in range(0,len(name)):
    name1 = name[i]
    findSql = f"SELECT * FROM travel WHERE name = '{name1}'"
    cur.execute(findSql)
    count = cur.rowcount
    if(count == 0):
        region1 = region[i]
        content1 = content[i]
        address1 = address[i]
        lat1 = lat[i]
        lon1 = lon[i]
        created_date = datetime.now()
        last_modified_date = datetime.now()
        id+=1
        imageUrl = travelImgInS3[i]
        saveSql = f"INSERT INTO travel (travel_id, name, location, info, address, latitude, longitude, created_date, last_modified_date, image) VALUES ({id},'{name1}', '{region1}' ,'{content1}','{address1}', '{lat1}','{lon1}', '{created_date}', '{last_modified_date}', '{imageUrl}');"
        cur.execute(saveSql)
        conn.commit()
conn.close()