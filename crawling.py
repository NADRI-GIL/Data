from selenium import webdriver
from bs4 import BeautifulSoup
import json
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pandas as pd

driver = webdriver.Chrome("")
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

for k in range(6, 10):
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

        # image = soup.find("img", class_="swiper-lazy swiper-lazy-loaded").get('src')
        # travel.append(image)
        # images = []
        # for j in range(len(image)):
        #     image = soup.find("img", class_="swiper-lazy swiper-lazy-loaded")
        #     images.append(image.get('src'))
        #
        # travel.append(images)

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

data.to_csv('여행지 지도.csv', index=False, encoding='cp949')
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
