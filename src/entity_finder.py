'''
Author: Antonio Norelli
NLP final project

entity_finder.py
Manages all the interactions with the babelnet APIs,
in particular it contains the functions that returns the relevant entities of a given query.
To find the entities are implemented two different strategies:
    1. babelfy_disambiguation, finds the entities using Babelfy.
    Generally better performance, faster and cheaper in babelcoins, but has some patologies (e.g. long questions with several entities)
    2. spacy_disambiguation, manually finds the entities considering the  POS tags and  the dependency grammar tags.
    Slower and more expensive in babelcoins but better on TIME, PLACE, PART and COLOR questions

If the code is executed standalone, it is provided an example of usage of the functions
'''


from requests import get
import urllib.parse
import urllib.request
import spacy  # spaCy is a library for advanced natural language processing in Python and Cython. https://spacy.io/docs/usage/


def get_entities_ids(text, domain=None, spacy_model=None, spacy_dis=False):
    """ Broker of the entity_finder functions

    Broker of the entity_finder functions, calls the appropriate entity finder according to the
    spacy_dis parameter

    Parameters:
        text - input text in which we want to find the entities
        domain - domain of interest, used to discard unrelated entities
        spacy_model - sapCy English NLP model for spacy_disambiguation
        spacy_dis - it explains itself

    Returns:
        entities_id - Dictionary of the finded entities in the format {'bn:00000000x': 'Trigger text'}
    """
    if spacy_dis:
        entities_id = spacy_disambiguaton(text, domain=domain, model=spacy_model)
        if not entities_id:
            entities_id = babelfy_disambiguation(text)
    else:
        entities_id = babelfy_disambiguation(text)
        if not entities_id:
            entities_id = spacy_disambiguaton(text, domain=domain, model=spacy_model)
    return entities_id


def babelfy_disambiguation(text):
    """ Function that uses Babelfy to find the entities in a text

    Analyzer of the response to the text of the Babelfy API,
    if two or more entities have words in common, only the longest entity is maintained

    Parameters:
        text - input text in which we want to find the entities

    Returns:
        entities_id - Dictionary of the finded entities in the format {'bn:00000000x': 'Trigger text'}
    """
    text = urllib.parse.quote_plus(text)
    response = get("https://babelfy.io/v1/disambiguate?"
                    "text={" + text + "}&"
                    "lang=EN&"
                    "matching=PARTIAL_MATCHING&"
                    "key=INSERT-BABELNET-KEY"
                   )
    text = urllib.request.unquote(text)
    json_response = response.json()
    entities_id = {}
    previous_entity_end, previous_entity_size, previous_entity_id = 0, 0, None
    for entity in json_response:
        entity_start = entity["tokenFragment"]["start"]
        entity_end = entity["tokenFragment"]["end"]
        entity_size = entity_end - entity_start
        if entity_start > previous_entity_end:
            entities_id[entity["babelSynsetID"]] = text[
                                                   entity["charFragment"]["start"] - 1:entity["charFragment"]["end"]]
        elif entity_size > previous_entity_size:
            entities_id.pop(previous_entity_id)
            entities_id[entity["babelSynsetID"]] = text[entity["charFragment"]["start"]:entity["charFragment"]["end"]]
        if (entity_end > previous_entity_end and entity_size > previous_entity_size) or entity_start > previous_entity_end:
            previous_entity_end, previous_entity_size = entity_end, entity_size
        previous_entity_id = entity["babelSynsetID"]
    return entities_id


def spacy_disambiguaton(text, domain=None, model=None):
    """ Function that manually finds the entities in a text using NLP techniques with spaCy

    Candidates for the relevant entities in a query are objects and subjects,
    subjects are filtered and only Nouns, Number and Proper nouns are maintained to avoid irrelevant words
    (e.g. What can be considered similar to X?, "What" is subject).
    Since spaCy analyzes only the single word, in order to find the complete entity
    is considered the full subtree containing the object/subject without articles "a", "an" and "the".
    The babelnetId of each entity is found using the Babelnet API.

    Parameters:
        text - input text in which we want to find the entities

    Returns:
        entities_id - Dictionary of the finded entities in the format {'bn:00000000x': 'Trigger text'}
    """
    if not model:
        print('\t\tloading model...')  # english nlp spacy model used for syntactic dependency parsing
        model = spacy.load('en')
        print('\t\tmodel loaded')
    analysis = model(text)
    entities_id = {}
    for word in analysis:
        if word.dep_[1:5] == 'subj' and word.pos_ in ['NOUN', 'NUM', 'PROPN']:
            chunk = ''
            for word1 in word.subtree:
                if word1.text not in ['the', 'a', 'an']:
                    chunk += word1.text + ' '
            chunk = chunk[:-1]  # removing last space
            babelnet_id = lemma_to_babelnetid(chunk, domain=domain)
            if babelnet_id:
                entities_id[babelnet_id] = chunk
        if word.dep_[1:4] == 'obj':
            chunk = ''
            for word1 in word.subtree:
                if word1.text not in ['the', 'a', 'an']:
                    chunk += word1.text + ' '
            chunk = chunk[:-1]  # removing last space
            babelnet_id = lemma_to_babelnetid(chunk, domain=domain)
            if babelnet_id:
                entities_id[babelnet_id] = chunk
    return entities_id


def babelnetid_to_lemma(id):
    """ takes a babelnetId, returns the corresponding lemma

    Babelnet getSynset API is used, it returns the "mainSense" of the babelnetId

    Parameters:
        id - babelnetId of which we want the lemma

    Returns:
        the lemma in a string
    """
    response = get("https://babelnet.io/v4/getSynset?"
                   "id=" + id + "&"
                    "key=INSERT-BABELNET-KEY"
                   )
    try:
        return response.json()["mainSense"]
    except KeyError:
        return ''


def check_id_domain(id, domain):
    """ checks if a babelnetId belongs to a domain

    Babelnet getSynset API is used, it checks if domain is in the "domains" of the babelnetId

    Parameters:
        id - babelnetId of which we want the lemma
        domain - domain of interest

    Returns:
        True if true, False if false, pretty straightforward
    """
    response = get("https://babelnet.io/v4/getSynset?"
                    "id=" + id + "&"
                    "key=INSERT-BABELNET-KEY"
                   )
    json_response = response.json()
    try:
        if domain.upper() in json_response["domains"]:
            return True
        else:
            return False
    except KeyError:
        print('babelnet_id', id, 'does not belong to', domain)
        return False


def lemma_to_babelnetid(lemma, domain=None):
    """ takes a lemma, returns the corresponding babelnetId

        Babelnet getSenses API is used, it returns the "id" of the first "synsetID"

        Parameters:
            id - babelnetId of which we want the lemma

        Returns:
            the lemma in a string
        """
    response = get("https://babelnet.io/v4/getSenses?"
                   "word=" + lemma + "&"
                    "lang=EN&"
                    "pos=NOUN&"
                    "key=INSERT-BABELNET-KEY"
                   )
    json_response = response.json()
    try:
        if domain:
            for item in json_response:
                id = item["synsetID"]["id"]  # Possible KeyError or TypeError
                if check_id_domain(id, domain):
                    return id
            return ''
        else:
            return response.json()[0]["synsetID"]["id"]  # Possible IndexError
    except (KeyError, TypeError, IndexError):
        return ''


def main():  # some examples
    print('Where is located the Statue of Liberty?', spacy_disambiguaton('Where is located the Statue of Liberty?'))
    print(get_entities_ids('Where is located the Tour Eiffel ?'))
    print('bn:00838523n', babelnetid_to_lemma('bn:00838523n'))

if __name__ == '__main__':
    main()




