import json
import requests
import datetime
from datetime import timedelta
from elasticsearch_dsl import A
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search


def package_ts_func_():

    es = Elasticsearch([("localhost:9200")])


    url = 'https://api.tripstore.kr/guest/list/places?cityId=1'
    # 모든 여행지 리스트를 모아 놓은 URL

    data = requests.get(url).text
    parsed_data = json.loads(data)
    # 여행지 URL을 파싱해서 정보를 가져옴

    lnth = len(parsed_data['list'])
    # lnth는 리스트의 길이, 여행지 장소 개수

    tday = datetime.datetime.now()
    today = tday.strftime("%Y-%m-%d")


    def monthdelta(date, delta):
        m, y = (date.month + delta) % 12, date.year + ((date.month) + delta - 1) // 12
        if not m: m = 12
        d = min(date.day, [31, 29 if y % 4 == 0 and not y % 400 == 0 
        else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
        return date.replace(day=d, month=m, year=y)
        # monthdelta 는 그 날로부터 몇달 후의 날짜를 호출해줌

    deletelist = []
    for i in range(0, lnth):
        city = (parsed_data['list'][i]['id'])
        # i 번째의 여행장소 ID를 프린트함
        s = Search(using=es, index="not_busy_list_package", doc_type='class')
        s = s.filter("term", cityId=city)
        s.aggs.metric('notbusy_stats', 'extended_stats', field='price')
        response = s.execute()
        meanprice = response.aggregations.notbusy_stats.avg
        meanprice = float(0 if meanprice is None else meanprice)
        stdprice = response.aggregations.notbusy_stats.std_deviation
        stdprice = float(0 if stdprice is None else stdprice)
        lowerlimit = meanprice - 2*stdprice
        res = es.search(index="not_busy_list_package", doc_type='class', body={
            "query": {"bool": {"must": [{"term": {"cityId": str(city)}}, {"term": {"today": today}}]}}}, 
                        scroll='3m', size=10000)
        for doc in res['hits']['hits']:
            todayprice = doc['_source']['price']
            if todayprice < lowerlimit and float(todayprice) < 2/3 * meanprice:
                deletelist.append(doc['_id'])

    print(deletelist)