'''
Author: Antonio Norelli
NLP final project

Relation_identifier.py
Finds the type of relation expressed in a given query,
this is accomplished using a support vector machine trained on the provided query patterns for each relation.
It is used a n-gram representation with unigrams and bigrams.
Concerning the implementation, the "Relation_identifier" class manages the classifier,
it prepares the dataset when invoked and has a "training" and "predict" method.

Commented code is used for a grid search to find the best parameters for the classifier.
'''


from sklearn.metrics import precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, chi2
from sklearn import svm
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report
from sklearn.linear_model import LogisticRegression



def svm_clf_training(max_features, data):
    """ Trainer of the SVM classifier

    Trainer of the SVM classifier.
    The data is vectorized, the best max_features are selected according to a chi2 test, and the classifier is trained.
    Commented code is used for a grid search to find the best parameters for the classifier.

    Parameters:
        max_features - maximum number of feature considered (size of the query-vector)
        data - dataset split in training and test

    Returns:
        clf - the trained classifier
        voc - the vocabulary of the unigrams and bigrams that are considered features
    """
    X_train, y_train, X_test, y_test = data
    clf = Pipeline([('feature_selection', SelectKBest(score_func=chi2, k=max_features)),
                    ('clf', svm.SVC(C=1., kernel='linear'))])

    vectorizer = CountVectorizer(ngram_range=(1, 2), lowercase=True)  # unigrams and bigrams
    X_matrix_tr = vectorizer.fit_transform(X_train)
    # parameters = [{'clf__kernel': ['linear'], 'clf__C': [0.1, 1, 10, 100]},
    #               {'clf__kernel': ['rbf'], 'clf__C': [0.1, 1, 10, 100], 'clf__gamma': [0.001, 0.01, 0.1]},
    #               {'clf__kernel': ['poly'], 'clf__C': [0.1, 1, 10, 100], 'clf__degree': [2, 3, 4, 5]}]
    # clf = GridSearchCV(svc, parameters, scoring='accuracy')
    clf.fit(X_matrix_tr, y_train)
    # print("Best parameters set found on development set:")
    # print()
    # print(clf.best_estimator_)
    # print()
    # print("Grid scores on development set:")
    # print()
    # for params, mean_score, scores in clf.grid_scores_:
    #     print("%0.3f (+/-%0.03f) for %r"
    #           % (mean_score, scores.std() / 2, params))
    # print()
    voc = vectorizer.get_feature_names()
    # vectorizer1 = CountVectorizer(ngram_range=(1, 2), lowercase=True, vocabulary=voc)
    # X_matrix_val = vectorizer1.fit_transform(X_test)
    # y_pred = clf.predict(X_matrix_val)

    # for i in range(len(X_test)):
    #     if y_test[i] != y_pred[i]:
    #         print(X_test[i], y_test[i], y_pred[i])
    # print(classification_report(y_test, y_pred))
    return clf, voc


def dataset_preparation():
    """ Prepares the dataset

    Prepares the dataset. Short query patterns are filtered out, a stratified division in training and test is returned

    Parameters:

    Returns:
        X_train, y_train, X_test, y_test - the ready-to-eat dataset
    """
    with open('../data/patterns_num.txt', 'r') as f:
        data = f.readlines()
        X, Y = [], []
        for line in data:
            x, y = line.split('\t')
            if len(x) > 5 and x not in X:  # better results are achieved excluding short query patterns
                X.append(x.replace("X", "").replace("Y", "").lower())
                Y.append(int(y.replace('\n', '')))
    test_size = 0.2
    # print('Test size:', test_size, '\nWrong classifications:\n')

    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=42, stratify=Y)
    return X_train, y_train, X_test, y_test

class RelationIdentifier():
    """ The working class :)

    Prepares the dataset when invoked,
    trains the classifier when training method is called,
    returns the predicted relation of a given text when the predict method is called
    """
    def __init__(self):
        self.dataset = dataset_preparation()
        self.model, self.voc = 0, 0
    def training(self):
        """ The training method.

        max_features = 'all' (all features maintained) guarantees the best results.
        Ok, I could have omitted the selectKbest step but who knew before? And maybe with another dataset is another story
        """
        self.model, self.voc = svm_clf_training('all', self.dataset)
        return 0
    def predict(self, text):
        """ The predict method

        Given a text, it is vectorized according to the vocabulary used during training and returns the predicted relation.
        Note that it is not necessary to remove the words belonging to the entities from a full query
        to obtain a sample more similar to the ones used in the training,
        since using the training vocabulary those words are ignored.

        Parameters:
            text - input query

        Returns:
            the id of the predicted relation
        """
        vectorizer = CountVectorizer(ngram_range=(1, 2), lowercase=True, vocabulary=self.voc)
        vector = vectorizer.fit_transform([text])
        return self.model.predict(vector)[0]





