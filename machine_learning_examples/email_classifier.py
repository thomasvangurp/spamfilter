#!/usr/bin/env python3.5
"""takes an input dataset in csv/tsv format that includes a column with a binary category variable
that we need to predict, allows user to specify the model and other parameters"""
import pandas
import numpy as np

from sklearn import ensemble
from sklearn.ensemble import RandomForestClassifier,AdaBoostClassifier, GradientBoostingClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.metrics import roc_curve, auc, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split


import matplotlib.pyplot as plt
import itertools
import codecs
import argparse
from string import punctuation

def parse_args():
    "Pass command line arguments"
    # if not sys.argv[1:]:
    #     sys.argv.append('-h')
    parser = argparse.ArgumentParser(description='Match predefined parameters for creating features from text data')
    parser.add_argument('-c','--category_ID',
                        help='category ID of the variable that is to be predicted',
                        default='spam')
    parser.add_argument('-i','--input',
                        help='input dataset in comma or tab separated txt',
                        default='/Users/thomasvangurp/enron-spam/output_v3.tsv')
    parser.add_argument('-s', '--seperator',
                        help='symbol that separates the entries',
                        default='\t')
    parser.add_argument('-m','--model',
                        help='scikit-learn model to use',
                        default='RandomForestClassifier')
    parser.add_argument('-r','--ratio',
                        help='ratio of input data to use for testing',
                        default='0.4')
    parser.add_argument('-o', '--output',
                        help='output directory for writing log file and outputs',
                        default='/Users/thomasvangurp/enron-spam/output/')
    args = parser.parse_args()
    return args


def load_data(args, input):
    """Load input data using pandas using codecs to correct for malformed characters"""
    with codecs.open(input, "r",encoding='utf-8', errors='ignore') as fdata:
        dataset = pandas.read_csv(fdata,sep='\t', header=0)
    #get dataset by looking for the column containing spam
    actual_category = dataset['spam']
    #remove the spam column from the dataset
    dataset.pop('spam')
    return dataset, actual_category



def plot_confusion_matrix(cm, classifier,args, classes,
                          normalize=True,title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    classifier_type = str(type(classifier)).split('.')[-1].rstrip(punctuation)
    plt.figure()
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)
    if normalize:
        cm = cm.astype(float) / cm.sum(axis=1)[:, np.newaxis]
        # for i in [0,1]:
        #     for j in [0,1]:
        #         cm[i][j] = '%.3f%%' % (100*cm[i][j])
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.savefig('/Users/thomasvangurp/enron-spam/confmat-100K-%s.pdf' % classifier_type)
    # plt.show()

def plot_roc(fpr, tpr, classifier):
    """plot Receiver Operator Characteristics curve"""
    classifier_type = str(type(classifier)).split('.')[-1].rstrip(punctuation)
    plt.figure()
    # Calculate the area under the curve for ROC
    roc_auc = auc(fpr, tpr)
    lw = 2
    plt.plot(fpr, tpr, color='darkorange',
             lw=lw, label='ROC curve (area = %0.4f)' % roc_auc)
    plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate (ham classified as spam)')
    plt.ylabel('True Positive Rate (ham correctly classified)')
    #TODO: make dynamic title depending on model type
    plt.title('Receiver operating characteristic 100K %s' % classifier_type)
    plt.legend(loc="lower right")
    plt.savefig('/Users/thomasvangurp/enron-spam/roc-100K-%s.pdf' % classifier_type)
    # plt.show()
    # print('boe')

def plot_parameter_performance(parameters):
    """plot parameter log odss"""
    return 0

def initialize_classifier(classifiers, args, parameters):
    """initialize a classifier instance"""
    for classifier in vars(classifiers):
        if classifier == args.model:
            #create instance and return it
            classifier = vars(classifiers)[classifier]()
            for parameter,setting in parameters.items():
                if parameter in vars(classifier):
                    if type(vars(classifier)[parameter]) == type(1) or vars(classifier)[parameter] == 'auto':
                        setting = int(setting)
                    else:
                        setting = str(setting)
                    if vars(classifier)[parameter] != 'auto':
                        assert type(setting) == type(vars(classifier)[parameter])
                    vars(classifier)[parameter] = setting
            return classifier

def print_stats(y_test, y_pred, y_train):
    """print output stats"""
    # print classification report
    print(classification_report(y_test, y_pred, target_names=['spam', 'ham']))
    # false positive is email classified as/predicted to be spam that is ham..
    false_positives_pct = 100 * len([i for i, j in zip(y_test, y_pred) if i == 0 and j == 1]) / \
                          float(len([i for i in y_test if i == 0]))
    # false negative is email classified as ham that is spam..
    false_negatives_pct = 100 * len([i for i, j in zip(y_test, y_pred) if i == 1 and j == 0]) / \
                          float(len([i for i in y_test if i == 1]))

    print('False positives: %.2f%%' % false_positives_pct)
    print('False negatives: %.2f%%' % false_negatives_pct)
    print('')
    print('emails used for training %s' % len(y_train))
    print('emails used for testing %s' % len(y_test))

def main():
    """main program routine"""
    args = parse_args()
    #todo: make more elegant option for determining that this our classified shouls be derived from sklearn.ensemble
    classifiers = ensemble
    #todo: add option to configure parameters from command-line
    parameters = {'n_estimators':30, 'max_features':80}
    #initialize classifier from command line arguments
    classifier = initialize_classifier(classifiers, args, parameters)
    #load data
    dataset, actual_category = load_data(args.input)
    # split dataset in a train and test set for validation
    X_train, X_test, y_train, y_test = train_test_split(
        dataset, actual_category, test_size=0.4, random_state=0)
    # from sklearn.naive_bayes import BernoulliNB
    # classifier = BernoulliNB()
    # classifier = RandomForestClassifier()
    # classifier = RandomForestClassifier(n_estimators=30, max_features=80)
    # classifier = AdaBoostClassifier(n_estimators=100)
    # train the model on the subset qualified for 'training'
    train_fit = classifier.fit(X_train, y_train)
    # predict the category of emails using our trained model on the test set
    y_pred = train_fit.predict(X_test)
    # get the probabilities (p-values) associated with these predictions
    y_prob = train_fit.predict_proba(X_test)[:, 1]
    # get vectors containing false positive rate, true positive rate and tresholds
    fpr, tpr, tresholds = roc_curve(y_test, y_prob)
    # plot roc curve
    plot_roc(fpr, tpr, classifier)

    #print stats
    print_stats(y_test, y_pred, y_train)
    # plot confusion matrix
    cnf_matrix = confusion_matrix(y_test, y_pred)
    plot_confusion_matrix(cnf_matrix, classifier,args, classes=['spam', 'ham'],
                          title='Confusion matrix, without normalization')


if __name__ == '__main__':
    main()