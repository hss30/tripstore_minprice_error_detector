from elasticsearch import Elasticsearch

es = Elasticsearch([("localhost:9200")])


deletelist = []
lnth = len(deletelist)

for i in range(0,lnth):
    es.delete(index="not_busy_list_package", doc_type='class', id=deletelist[i])