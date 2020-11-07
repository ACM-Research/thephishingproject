""" Module for interpreting and visualizing already parsed data.

Loads data from processed_data/analyzer_script/phishing_analysis.json and non_phishing_analysis.json

When it becomes helpful to view data on an x-y plane (i.e. for regression) phishing emails will be given
a y-value of 1 and non-phishing emails will be given a value of 0.
"""
import json
from os import path
import matplotlib.pyplot as pyplot
import numpy as np
from numpy.linalg import lstsq

import tests
from tests import TestType

# Constants
ROOT = path.abspath(path.join(path.dirname(__file__), "../.."))
NON_PHISH_PATH = path.join(ROOT, "processed_data",
                           "analyzer_script", "non_phishing_analysis.json")
PHISH_PATH = path.join(ROOT, "processed_data",
                       "analyzer_script", "phishing_analysis.json")
NON_PHISH_VAL = -1
PHISH_VAL = 1

# Load jsons into arrays of emails
phish_emails = []
non_phish_emails = []

with open(PHISH_PATH, "r") as phish_info:
    phish_dict = json.load(phish_info)
    phish_emails = list(phish_dict.values())

with open(NON_PHISH_PATH, "r") as non_phish_info:
    non_phish_dict = json.load(non_phish_info)
    non_phish_emails = list(non_phish_dict.values())

def graphBarMulti(phishingResults: list, nonPhishingResults: list, testName=""):
    email_services = ["hotmail", "gmail", "yahoo", "aol", "msn","icloud"]
    allCategories = list(set(phishingResults) | set(
        nonPhishingResults))  # union of unique category values
    # 1 is public domain, 2 is private domain
    phishData1 = {}
    phishData2 = {}
    nonPhishData1 = {}
    nonPhishData2 = {}
    for category in allCategories:
        if any(email_service in category for email_service in email_services):
            phishData1[category] = phishingResults.count(category)
            nonPhishData1[category] = nonPhishingResults.count(category)
        else:
            phishData2[category] = phishingResults.count(category)
            nonPhishData2[category] = nonPhishingResults.count(category)
    N = 2
    phishData1 = list(filter((0).__ne__, (list(phishData1.values()))))
    phishData2 = list(filter((0).__ne__, (list(phishData2.values()))))
    nonPhishData1 = list(filter((0).__ne__, (list(nonPhishData1.values()))))
    nonPhishData2 = list(filter((0).__ne__, (list(nonPhishData2.values()))))
    tP = len(phishData1)+len(phishData2)
    tNP = len(nonPhishData1)+len(nonPhishData2)
    pyplot.ylim((0,100))
    phishData = (len(phishData1)/tP*100, len(phishData2)/tP*100)
    nonphishData = (len(nonPhishData1)/tNP*100,len(nonPhishData2)/tNP*100)
    ind = np.arange(N)
    width = 0.35

    pyplot.bar(ind, phishData, width, label='Phishing')
    pyplot.bar(ind + width, nonphishData, width, label='Non-Phishing')

    pyplot.ylabel('Percentage of Emails')
    pyplot.title(testName)

    pyplot.xticks(ind + width / 2, ('Public Domain','Private Domain'))
    pyplot.legend(loc='best')
    pyplot.show()


def graphCategorical(phishingResults: list, nonPhishingResults: list, testName=""):
    """ Graphs categorical results based on quanitity for each of the two separate categories.

    Infers category names from those found among the results. As a result, if a valid category
    is not represented among the results it will not be graphed or labeled.
    """
    allCategories = list(set(phishingResults) | set(
        nonPhishingResults))  # union of unique category values
    phishData = {}
    nonPhishData = {}
    for category in allCategories:
        # this counting algorithm is inefficient (multiple passes)
        phishData[category] = phishingResults.count(category)
        nonPhishData[category] = nonPhishingResults.count(category)
    # graph
    N = max(len(phishData.keys()), len(nonPhishData.keys()))  # number of categories on x axis
    tP = sum(phishData.values())  # total of Phishing Emails
    tNP = sum(nonPhishData.values())  # total of non-Phishing Emails
    valuePH = [data/tP*100 for data in phishData.values()]  # Gets the percentage of each category
    valueNPH = [data/tNP*100 for data in nonPhishData.values()]

    ind = np.arange(N)
    width = 0.35
    pyplot.ylim(0, 100)
    pyplot.bar(ind, valuePH, width, label='Phishing')
    pyplot.bar(ind+width, valueNPH, width, label='Non-Phishing')
    pyplot.ylabel('Percentage')
    pyplot.title(testName)
    pyplot.xticks(ind + width / 2, (phishData.keys()))
    pyplot.legend(loc='best')
    pyplot.show()



def graphNumerical(phishingResults: list, nonPhishingResults: list, testName=""):
    """ Graphs numerical results for each of the categories.

    There are multiple ways to represent this data but for now we use a histogram
    """
    nBins = 20

    pyplot.hist(phishingResults, nBins, alpha=0.5, label="Phishing")
    pyplot.hist(nonPhishingResults, nBins, alpha=0.5,  label="Non-Phishing")
    pyplot.title(testName)
    pyplot.legend()
    pyplot.show()

def graphBestFit(phishingResults: list, nonPhishingResults: list, testName=""):
    """ Use least squares to fit a linear trend to the results.

    Phishing emails are given a score of 1 while legitamate emails are given a score of -1.
    """
    # format for approximating system Ax = b
    matA = phishingResults + nonPhishingResults
    vecB = [PHISH_VAL] * len(phishingResults) + [NON_PHISH_VAL] * len(nonPhishingResults)
    
    predX, residuals, rank, singulars = lstsq(matA, vecB, rcond = None)
    predResults = np.dot(matA, predX)

    phishPredictions = predResults[:len(phishingResults)]
    nonPhishPredictions = predResults[len(phishingResults):]
    graphNumerical(phishPredictions, nonPhishPredictions, "Best Fit: "+testName)


def visualizeTest(test):
    """ Graphs test according to type. 

    Test must be a function that takes a single email as argument and has member
    fields .testType and .testName
    """
    # run tests for all
    phishingResults = [test(email) for email in phish_emails]
    nonPhishingResults = [test(email) for email in non_phish_emails]

    # graph according to type
    if test.testType == TestType.categorical:
        graphCategorical(phishingResults, nonPhishingResults, test.testName)

    elif test.testType == TestType.numerical:
        graphNumerical(phishingResults, nonPhishingResults, test.testName)

    elif test.testType == TestType.bestfit:
        graphBestFit(phishingResults, nonPhishingResults, test.testName)
    elif test.testType == TestType.domain:
        graphBarMulti(phishingResults, nonPhishingResults, test.testName)


if __name__ == "__main__":
    for test in allTests:
        visualizeTest(test)
