import schedule
import time
import tripstore_airtel_price_elasticsearch
import tripstore_airtel_price_busyfilter
import tripstore_airtel_price_twosigmatest

def job1():
    return tripstore_airtel_price_elasticsearch.airtel_elasticsearch()
    # minprice1의 함수를 불러옴

def job2():
    return tripstore_airtel_price_busyfilter.airtel_busy_filter()
    # minprice1의 함수를 불러옴

def job3():
    return tripstore_airtel_price_twosigmatest.airtel_ts_func_()
    # minprice1의 함수를 불러옴


schedule.every().day.at("09:50").do(job1)
schedule.every().day.at("10:50").do(job2)
schedule.every().day.at("11:50").do(job3)


while True:
    schedule.run_pending()
    time.sleep(1)