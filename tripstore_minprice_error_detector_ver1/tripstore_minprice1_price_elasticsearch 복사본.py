import json
import requests
import datetime
import elasticsearch


#def minprice1_elasticsearch():
url = 'https://api.tripstore.kr/guest/list/places?cityId=1'
# 모든 여행지 리스트를 모아 놓은 URL

data = requests.get(url).text
parsed_data = json.loads(data)
# 여행지 URL을 파싱해서 정보를 가져옴

lnth = len(parsed_data['list'])
# lnth는 리스트의 길이, 여행지 장소 개수

dt = datetime.datetime.now()
today = dt.strftime("%Y%m%d")
todaystring = dt.strftime("%Y-%m-%d")



for i in range (0,lnth):
    cityId = (parsed_data['list'][i]['id'])
    # i 번째의 여행장소 ID를 프린트함
    print(cityId)
    placeName = (parsed_data['list'][i]['placeName'])
    placeCode = (parsed_data['list'][i]['placeCode'])
    # i 번째의 여행장소 이름과 코드를 기록함
    url2 = 'https://api.tripstore.kr/guest/list/calendar?cityId=1&placeId=' + str(cityId) + '&path=search'
    # i 번째의 여행장소 id로 여행 시작 날짜 및 가격들을 포함하고 있는 URL을 만듦
    data2 = requests.get(url2).text
    parsed_data2 = json.loads(data2)
    # URL 정보들을 파싱하고 웹에 나오는 사이즈를 lnth2에 기록
    lnth2 = len(parsed_data2['list'])
    url3 = 'http://localhost:9200/minprice1/class/'
    for j in range (0,lnth2):
        price1 = parsed_data2['list'][j]['price']
        startday=parsed_data2['list'][j]['date']
        startday1=datetime.datetime.strptime(startday, '%Y-%m-%d')
        startday2=startday1.strftime("%Y%m%d")
        #print(startday2)
        # 여행지의 여행 출발 날짜들과 가격 등을 기록함
        url4 = url3 + str(today) + str(startday2) + str(cityId)
        url5 = 'http://localhost:9200/not_busy_list/class'
        url6 = url5 + str(today) + str(startday2) + str(cityId)
        #print(url4)
        data3 = {"cityId": str(cityId), "placeCode": str(placeCode), "placeName": str(placeName),
                 "today":str(todaystring), "startdate":str(startday), "price": int(price1)}
        # 여행지 정보 및 검색 날짜, 여행 출발 날짜 등으로 고유 id를 만들고 기록할 정보들을 json 형식으로 만듦
        requests.post(url4, json=data3)
        requests.post(url6, json=data3)
        # 만들어진 json을 http에 post함



print("done")
# post가 끝나면 끝났다고 프린트함
