'''
Author: Antonio Norelli
NLP final project

performance_evaluation.py
Generates the suitable test set and then the scores for the entity finder and the relation identifier.
'''


from Relation_identifier import RelationIdentifier
from Answerer import dataset_dicts, relation_id_dict
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, classification_report
import itertools
from entity_finder import get_entities_ids, babelnetid_to_lemma
import spacy
import random

random.seed(42)

dataset = dataset_dicts()

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    if normalize:
        cm = cm.astype('float') * 100 / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    # print(cm)

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=90)
    plt.yticks(tick_marks, classes)

    fmt = '.0f' if normalize else 'd'
    # fmt = '.2f' if normalize else 'd'
    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, format(cm[i, j], fmt),
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')


def evaluation_relation_identifier(dataset):
    rel_id_dict = relation_id_dict()
    id_relation = {v: k for k, v in rel_id_dict.items()}
    relations_occurrences = {k: 100 for k in rel_id_dict.keys()}
    relation_identifier = RelationIdentifier()
    relation_identifier.training()

    test_samples = []
    for entry in dataset:
        # if entry["answer"].lower() not in ['yes', 'no']:
        relation = entry["relation"]
        if relations_occurrences[relation]:
            test_samples.append(entry)
            relations_occurrences[relation] -= 1
        if all(value == 0 for value in relations_occurrences.values()):
            break
    test_samples = list(sorted(test_samples, key=lambda k: k['relation']))

    y_true, y_pred = [], []
    for sample in test_samples:
        y_true.append(sample["relation"])
        y_pred.append(id_relation[relation_identifier.predict(sample["question"])])
        last_t = y_true[-1]
        last_p = y_pred[-1]
        if last_p != last_t:
            print(last_t, last_p, sample["question"])


    cnf_matrix = confusion_matrix(y_true, y_pred)

    np.set_printoptions(precision=2)

    # Plot non-normalized confusion matrix
    plt.figure()
    # plot_confusion_matrix(cnf_matrix, classes=sorted(relations_occurrences.keys()), title='Confusion matrix, without normalization')
    plot_confusion_matrix(cnf_matrix, classes=sorted(relations_occurrences.keys()), title='Confusion matrix, with normalization', normalize=True)
    # Plot normalized confusion matrix
    # plt.figure()
    # plot_confusion_matrix(cnf_matrix, classes=relations_occurrences.keys(), normalize=True, title='Normalized confusion matrix')
    print(classification_report(y_true, y_pred))
    plt.show()


def evaluation_entity_identifier(dataset):
    random.shuffle(dataset)
    print('\t\tloading model...')  # english nlp spacy model used for syntactic dependency parsing
    model = spacy.load('en')
    print('\t\tmodel loaded')
    rel_id_dict = relation_id_dict()
    relations_occurrences = {k: 5 for k in rel_id_dict.keys()}

    test_samples = []
    for entry in dataset:
        # if entry["answer"].lower() not in ['yes', 'no']:
        relation = entry["relation"]
        if relations_occurrences[relation] and entry["answer"].lower() not in ['yes', 'no']:
            test_samples.append(entry)
            relations_occurrences[relation] -= 1
        if all(value == 0 for value in relations_occurrences.values()):
            break
    test_samples = list(sorted(test_samples, key=lambda k: k['relation']))

    total_correct_prediction = 0
    print('score\tbID1\tbID2\tpredicted_entities\tquery')
    for sample in test_samples:
        entities_correspondence = 0
        predicted_entities = get_entities_ids(sample["question"], spacy_dis=False, spacy_model=model)
        if sample["c1"] in predicted_entities or sample["c2"] in predicted_entities:
            entities_correspondence = 1
            total_correct_prediction += 1
        print(entities_correspondence, '\t', sample["c1"], '\t', sample["c2"], '\t', predicted_entities, '\t', sample["question"])
    print('\ntotal score:', total_correct_prediction, '/', len(test_samples), '\t', float(total_correct_prediction*100)/len(test_samples), '%')

def dataset_consistency(dataset):
    random.shuffle(dataset)
    print('\t\tloading model...')  # english nlp spacy model used for syntactic dependency parsing
    model = spacy.load('en')
    print('\t\tmodel loaded')
    rel_id_dict = relation_id_dict()
    relations_occurrences = {k: 5 for k in rel_id_dict.keys()}

    test_samples = []
    for entry in dataset:
        # if entry["answer"].lower() not in ['yes', 'no']:
        relation = entry["relation"]
        if relations_occurrences[relation] and entry["answer"].lower() not in ['yes', 'no']:
            test_samples.append(entry)
            relations_occurrences[relation] -= 1
        if all(value == 0 for value in relations_occurrences.values()):
            break
    test_samples = list(sorted(test_samples, key=lambda k: k['relation']))

    for entry in test_samples:
        print(entry['relation'], '\t', entry["question"], '\t', babelnetid_to_lemma(entry["c1"]), '\t', babelnetid_to_lemma(entry['c2']))

def main():
    dataset_consistency(dataset)
    evaluation_entity_identifier(dataset)
    evaluation_relation_identifier(dataset)
if __name__ == '__main__':
    main()
