import json
import requests
import datetime
from datetime import timedelta
from elasticsearch import Elasticsearch
import elasticsearch.helpers


#def airtel_busy_filter():

# Busy filter는 최저 가격이 매우 가파르게 오르는 성수기 (2월 1일 근처 설날 연휴: 1월 30일 ~ 2월 3일), 그리고 6개월 째의 정보들을 걸러낸다.
# 6개월 후의 최저가 패키지 여행 상품 정보들은 소수여서 최저 가격들의 평균과 표준 편차를 계산하는데에 적합하지 않은 데이터다.
# (하나투어 상품들 중 최저가인 경우가 대부분이다. 그래서 '최저가'라고 하기에는 부족한 감이 있다.)
# 6개월 후의 상품 가격들은 나중에 가격 경향을 분석하는데에는 적합 할 수 있지만 위에서 언급했듯이, 대체적으로 하나투어를 제외한 여행사들은 현재로부터 6개월
# 후의 패키지 상품들을 업데이트 하지 않는다. (특히 에어텔)
#
# 일단 여행 출발 6개월 전에 패키지 상품을 예약 하는 사람들은 극소수가 아닐까....


def monthdelta(date, delta):
    m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
    if not m: m = 12
    d = min(date.day, [31,
                       29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][
        m - 1])
    return date.replace(day=d, month=m, year=y)
    # monthdelta 는 그 날로부터 몇달 후의 날짜를 호출해줌



busy_list = ['2019-01-31', '2019-02-01', '2019-02-02', '2019-02-03']
# busy_list는 비정상적으로 비싼 성수기의 날짜들을 넣은 리스트

firstesday = '2018-10-29'
# 가격 정보를 처음 기록한 날짜
tday = datetime.datetime.now()
today = tday.strftime("%Y-%m-%d")
firstesday_object = datetime.datetime.strptime(firstesday, '%Y-%m-%d')
today_object = datetime.datetime.strptime(today, '%Y-%m-%d')
deltatoday = today_object-firstesday_object

today_list = []
for i in range(deltatoday.days+1):
    today_list.append((firstesday_object+timedelta(i)).strftime("%Y-%m-%d"))
    #today_list: 데이터를 입력한 날짜들을 모은 리스트

es = Elasticsearch([("localhost:9200")])


# 처음 했을 때:
# elasticsearch.helpers.reindex(es, "airtel", "not_busy_list_airtel", target_client=es)
# airtel에 있는 모든 정보들을 복사해서 not_busy_list_airtel라는 인덱스를 새로 생성하여 복붙함
# 하지만 이미 입력한 상황에서는 엘라스틱서치 에서 airtel에 넣을 때 동시에 not_busy_list_airtel에 넣음

for i in range(0, len(busy_list)):
    res = es.search(index="not_busy_list_airtel", doc_type='class', 
                    body={"query":{"bool":{"must":[{"term":{"startdate":busy_list[i]}}]}}}, 
                    scroll = '3m', size = 10000)
    #res = es.search(index="not_busy_list_airtel", doc_type='class', body={
    #    "query": {"bool": {"must": [{"term": {"startdate": busy_list[i]}}, {"term": {"today": today}}]}}},
    #                scroll='3m', size=10000)
    # not_busy_list 안에 있는 정보들 중 출발 날짜가 성수기인 것들을 모조리 search 함
    for doc in res['hits']['hits']:
        # 찾은 서치들의 정보들을 doc 이라고 함
        res1 = es.get(index="not_busy_list_airtel", doc_type='class', id=doc['_id'])
        # 성수기 출발상품을 포함하는 아이디들을 호출
        doc1 = res1['_source']
        # 성수기 출발 상품들의 내용이 doc1
        res2 = es.index(index="busydays_airtel", doc_type='class', id=doc['_id'], body=doc1)
        # busydays라는 인덱스를 생성하고 동일한 id로 성수기 출발 상품들의 내용을 집어 넣음
        es.delete(index="not_busy_list_airtel", doc_type='class', id=doc['_id'])
        # not_busy_list에서 성수기 때 출발하는 상품들의 id들을 삭제함
        # 이로서 성수기 필터 완료



for i in range(0, len(today_list)):
    # 6개월 후의 상품들을 모두 삭제
    datetime_object = datetime.datetime.strptime(today_list[i], '%Y-%m-%d')
    #datetime_object = datetime.datetime.strptime(today, '%Y-%m-%d')
    five_after = monthdelta(datetime_object, 5)
    six_after = monthdelta(datetime_object, 6)
    firstday = five_after.replace(day=1)
    # 삭제가 시작하는 날 (예시 : 10월 29일 기록한 정보라면 3월 1일 이후 출발하는 상품들의 정보를 모두 삭제)
    lastday = six_after.replace(day=1) - datetime.timedelta(days=1)
    delta = lastday - firstday
    daylist = []
    # 삭제해야하는 상품들의 출발일로 이루어진 리스트
    for j in range(delta.days + 1):
        d1 = firstday + timedelta(j)
        daylist.append(d1)
        daylist[j] = daylist[j].strftime('%Y-%m-%d')
        # 날짜들을 datetime 에서 str 으로 변환
        #res = es.search(index="not_busy_list_airtel", doc_type='class', body={
        #    "query": {"bool": {"must": [{"term": {"startdate": daylist[j]}}, {"term": {"today": today}}]}}},
        #                scroll='3m',
        #                size=10000)
        res = es.search(index="not_busy_list_airtel", doc_type='class', 
                        body={"query": {"bool": {"must": [{"term": {"startdate": daylist[j]}}, 
                                                          {"term": {"today": today_list[i]}}]}}}, 
                        scroll='3m', size=10000)
        # 엘라스틱 서치로 삭제해야 하는 상품들을 검색함
        for doc in res['hits']['hits']:
            es.delete(index="not_busy_list_airtel", doc_type='class', id=doc['_id'])
            # 삭제해야 하는 상품들의 아이디를 이용하여 상품 삭제

