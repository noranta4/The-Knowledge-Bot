'''
Author: Antonio Norelli
NLP final project

babelnet_id_cleaner.py
Standardizes the data in dataset.json, the clean dataset is stored in clean_dataset.json
'''


import json
with open('../data/dataset.json', encoding="utf8") as json_data:
    dicts = json.load(json_data)
with open('../data/clean_dataset.json', 'w', encoding="utf8") as f:
    flag = 0  # first item with a '[' instead of a ','
    for dict in dicts:
        # c1 and c2 format is very various, here it is searched and maintained only the babelnet id
        control = 0
        bid_bad_1 = dict['c1']
        bid_bad_2 = dict['c2']
        for i in range(len(bid_bad_1)):
            if bid_bad_1[i:i+3] == 'bn:' or bid_bad_1[i:i+3] == 'bn_':
                bid_1 = bid_bad_1[i:i+12].replace('_', ':')
                control += 1
                break
        for i in range(len(bid_bad_2)):
            if bid_bad_2[i:i + 3] == 'bn:' or bid_bad_1[i:i+3] == 'bn_':
                bid_2 = bid_bad_2[i:i + 12].replace('_', ':')
                control += 1
                break
        if control == 2:  # if both babelnet ids are detected
            if flag == 1:
                s = ',{"question":"' + dict['question'].replace('"', "'") + \
                    '","answer":"' + dict['answer'].replace('\"', "'") + \
                    '","relation":"' + dict['relation'] + \
                    '","c1":"' + bid_1 + \
                    '","c2":"' + bid_2 + '"}\n'
            else:
                s = '[{"question":"' + dict['question'].replace('"', "'") + \
                    '","answer":"' + dict['answer'].replace('\"', "'") + \
                    '","relation":"' + dict['relation'] + \
                    '","c1":"' + bid_1 + \
                    '","c2":"' + bid_2 + '"}\n'
                flag = 1
            f.write(s)
    f.write(']')
