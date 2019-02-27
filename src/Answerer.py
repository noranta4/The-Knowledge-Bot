'''
Author: Antonio Norelli
NLP final project

Anwerer.py
Core of the project,
the class Answerer contains the method "answer" that given a couple (query, domain) returns an answer;
and contains the method "query" that given a domain returns a query about something not in the dataset.
All the other functions gather the necessary data: (these are not individually commented since are self explanatory)
    1. babelnetId - domain dictionary
    2. relation - relationId dictionary
    3. domain - relation dictionary
    4. relation - queries dictionary
    5. domain list
    6. disambiguator choice
    7. knowledge base dataset stored in a list of dictionaries

If the code is executed standalone, it is provided an example of usage of the functions
'''


from entity_finder import get_entities_ids, babelnetid_to_lemma
from Relation_identifier import RelationIdentifier
import json
import random
import spacy

#random.seed(42)

def babelnetid_domain_dict():
    id_domain_file = "../data/babeldomains_babelnet.txt"
    id_dom_dict = {}
    with open(id_domain_file) as f:
        for line in f:
            items = line.replace("\n", "").split("\t")
            id_dom_dict[items[0]] = [items[1]] + [more_domain for more_domain in items[3:]]
    return id_dom_dict


def relation_id_dict():
    with open('../data/relations.txt') as f:
        relation_id = {}
        for line in f.readlines():
            split_line = line.split('\t')
            relation_id[split_line[1].upper().replace('\n', '')] = int(split_line[0])
    return relation_id


def domain_relations_dict():
    with open('../data/domain_relations.txt') as f:
        dom_rel = {}
        for line in f.readlines():
            split_line = line.split('\t')
            dom_rel[split_line[0]] = split_line[1].split()
    return dom_rel


def relation_questions_dict():
    with open('../data/patterns_num.txt') as f:
        rel_quest = {}
        for line in f.readlines():
            split_line = line.split('\t')
            if 'Y' not in split_line[0]:
                try:
                    rel_quest[int(split_line[1].replace('\n', ''))].append(split_line[0])
                except KeyError:
                    rel_quest[int(split_line[1].replace('\n', ''))] = [split_line[0]]
    return rel_quest


def domains_list():
    with open('../data/domain_list.txt') as f:
        domains = []
        for line in f.readlines():
            domains.append(line.replace('\n', ''))
    return domains


def disambiguator_choice(relation_id):
    if relation_id in [1, 3, 8, 16]:  # if relation is COLOR, PLACE, PART or TIME
        return True  # spacy disambiguator
    else:
        return False  # babelfy disambiguator


def dataset_dicts():
    with open('../data/clean_dataset.json', encoding="utf8") as json_data:
        pentaple_dicts = json.load(json_data)
    return pentaple_dicts

class Answerer():
    """ The core of the model

    Contains the method "answer" that given a couple (query, domain) returns an answer;
    and contains the method "query" that given a domain returns a query about something not in the dataset.
    """
    def __init__(self):
        self.relation_identifier = RelationIdentifier()  # relation identifier classifier to find the relation of a query
        self.relation_identifier.training()  # trained
        self.id_domains = babelnetid_domain_dict()  # babelnetId - domain dict
        self.relation_id = relation_id_dict()  # relation - relationId dict
        self.id_relation = {v: k for k, v in self.relation_id.items()}  # and its inverse
        self.knowledge_dataset = dataset_dicts()  # dataset list of dicts
        self.domain_rel = domain_relations_dict()  # domain - relation dict
        self.rel_quest = relation_questions_dict()  # relation - queries dict
        self.spacy_nlp_model = spacy.load('en')  # spaCy NLP model

    def answer(self, query, domain):
        """ The answer method

        Given a query and a domain,
        predicts the relation,
        finds all entities (babelnetId) contained,
        filters out entities not relevant with the given domain,
        given the predicted relation and the entities found, searches for an answer in the dataset and returns it.

        Parameters:
            query - input query
            domain - chosen domain

        Returns:
            answer -  a string containing the answer
        """
        predicted_relation = self.relation_identifier.predict(query)
        all_babelnetids = get_entities_ids(query, domain=domain, spacy_model=self.spacy_nlp_model,
                                           spacy_dis=disambiguator_choice(predicted_relation))
        relevant_babelnetids = {}
        for id in all_babelnetids:
            try:
                if domain in self.id_domains[id]:
                    relevant_babelnetids[id] = all_babelnetids[id]
            except KeyError:  # if the id is not in babeldomains_babelnet.txt
                pass
        print('\t\tQuery:', query)
        print('\t\tPredicted relation:', self.id_relation[predicted_relation])
        print('\t\tEntities detected:', relevant_babelnetids)
        answer = None
        if not all_babelnetids:  # no entities detected
            answer = "Sorry, I don't understand the object of your question"
            return answer
        if not relevant_babelnetids:  # all entities detected are removed since not relevant with the domain
            answer = 'Your question is not about ' + domain
            return answer
        else:  # there is at least one relevant entity
            for pentaple in self.knowledge_dataset:  # search for an answer in the dataset
                if len(relevant_babelnetids) == 1:
                    if (predicted_relation == self.relation_id[pentaple["relation"]]) and (
                                (pentaple["c1"] in relevant_babelnetids) or (pentaple["c2"] in relevant_babelnetids)):
                        answer = pentaple["answer"]
                        break
                else:
                    if (predicted_relation == self.relation_id[pentaple["relation"]]) and (
                                pentaple["c1"] in relevant_babelnetids) and (pentaple["c2"] in relevant_babelnetids):
                        answer = pentaple["answer"]
                        break
        if not answer:  # no answer found
            answer = 'Sorry, I have not an answer for this question'
        return answer

    def query(self, domain):
        """ The query method

        Given a domain,
        scrolls in a random order the babelnetIds in the babelnetId-domain dictionary,
        if a babelnetId is of the chosen domain, chooses a relation relevant to the domain,
        chooses a random query pattern among the ones available for the chosen relation,
        formulates the question inserting the babelnetId lemma into the query pattern,
        raises the question to the "answer" method,
        if the answer is 'Sorry, I have not an answer for this question'
        (question with a sense and understood, but without an answer in the dataset),
        returns the question with the chosen relation and the entity (babelnetId).

        Parameters:
            domain - chosen domain

        Returns:
            a dict with the question, its relation and its entity
        """
        shuffled_id_list = list(self.id_domains.keys())
        random.shuffle(shuffled_id_list)
        for id in shuffled_id_list:
            if domain in self.id_domains[id]:
                relation_chosen = random.choice(self.domain_rel[domain])
                id_lemma = babelnetid_to_lemma(id).replace('_', ' ')
                if id_lemma:
                    question = random.choice(self.rel_quest[self.relation_id[relation_chosen]]).replace('X', id_lemma)
                    print("\tPossible question:")
                    auto_answer = self.answer(question, domain)
                    if auto_answer == 'Sorry, I have not an answer for this question':
                        print("\tQuestion found")
                        return {"query": question, "relation": relation_chosen, "c1": id}
                    else:
                        print("\tQuestion discarded, the bot already knows the answer or it did not understand the question")


def main():  # some examples
    a = Answerer()
    print(a.answer('Where is Tour Eiffel ?', 'Art, architecture, and archaeology'))
    print(a.query('Games and video games'))

if __name__ == '__main__':
    main()

