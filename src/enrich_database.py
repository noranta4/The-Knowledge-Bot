'''
Author: Antonio Norelli
NLP final project

enrich_database.py
manages the requests of updating of the dataset with the user answers
and practically updates the KBS server when executed standalone.
'''


import json
import requests
from entity_finder import get_entities_ids


def enrich_database(query, answer, domain, relation, c1):
    """ Enrich the database with the provided data

    If the user answer is useful all the elements of the question are saved on a file in a convenient json format.
    All the data is provided in input except the entity (babelnetId) in the user answer, that is processed here.

    Parameters:
        query - input query
        answer - user answer
        domain - chosen domain
        relation - chosen relation
        c1 - babelnetId of the entity in the query

    Returns:
        True if the dataset is enriched, False if not
    """
    print('\t\tUser answer:', answer)
    if answer in ['Question is misplaced', 'Sorry, I have not an answer for this question']:
        return False
    else:
        with open('../data/enriching_database.txt', 'a') as f:
            data = {}
            try:
                entities_detected = get_entities_ids(answer, spacy_dis=True)
                print('\t\tEntities detected:', entities_detected)
                c2 = list(entities_detected.keys())[0]  # if more entities are detected, the first is chosen
                print("\tSUCCESS: database enriched")
            except IndexError:
                print('FAIL: Database not enriched, Entity in the answer not detected\n')
                return False
            data["question"] = query
            data["answer"] = answer
            data["relation"] = relation
            data["context"] = "enriching"
            data["domains"] = domain
            data["c1"] = c1
            data["c2"] = c2
            f.write(json.dumps(data))
            f.write('\n')
            print('\t\t', data, '\n')
        return True


def main():
    """ Send new data to the KBS server

    If there is something to add to the KBS (the raw_data_file is not empty),
    all the data is saved in a new json file (json_data_file) that will correspond to the KBS update,
    the data is uploaded in the KBS,
    all the data in the raw_data_file is finally erased.
    """
    raw_data_file = '../data/enriching_database.txt'
    json_data_file = '../data/enriching_database.json'
    with open(raw_data_file, 'r', encoding="utf8") as raw_data:
        lines = raw_data.readlines()
    if lines:
        with open(json_data_file, 'w', encoding="utf8") as raw_to_json_data:
            raw_to_json_data.write('[')
            raw_to_json_data.write(lines[0])
            for i_line in range(1, len(lines)):
                raw_to_json_data.write(',' + lines[i_line])
            raw_to_json_data.write(']')
        with open(json_data_file, 'r', encoding="utf8") as json_data:
            parsed_data = json.load(json_data)
            r = requests.post(
                'http://151.100.179.26:8080/KnowledgeBaseServer/rest-api/add_items_test?key=INSERT-BABELNET-KEY',
                json=parsed_data)
            if r.text == '1':
                print("KBS enriched successfully")
            else:
                print("Error:\n", r.text)
        with open(raw_data_file, 'w', encoding="utf8"):
            pass


if __name__ == '__main__':
    main()

