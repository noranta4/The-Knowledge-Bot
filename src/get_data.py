'''
Author: Antonio Norelli
NLP final project

get_data.py
Collects the data from the knowledge base server and store it in a convenient json format in dataset.json
The queries with answer = 'no' are excluded
'''


import urllib.request
import json

counter = 0
with open('../dataset.json', 'w') as f:
    f.write('[')
    for id_number in range(0,1000000,5000):
        if id_number % 10000 == 0:
            print(id_number)
        url = 'http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/items_from?id=' + str(id_number) + \
              '&key=INSERT-BABELNET-KEY'
        req = urllib.request.Request(url)

        # parsing response
        r = urllib.request.urlopen(req).read()
        cont = json.loads(r.decode('utf-8'))

        # parsing json
        for item in cont:
            if item['answer'].lower() != 'no':
                f.write(json.dumps(item) + ',\n')
                counter += 1
    f.write(']')

print("Number of documents: ", counter)