""" Module for interpreting and visualizing already parsed data.

Loads data from processed_data/analyzer_script/phishing_analysis.json and non_phishing_analysis.json

When it becomes helpful to view data on an x-y plane (i.e. for regression) phishing emails will be given
a y-value of 1 and non-phishing emails will be given a value of 0.
"""
import matplotlib.pyplot as pyplot
import numpy as np
from numpy.linalg import lstsq

import tests
from tests import TestType

from data import runTestOnAll, PHISH_VAL, NON_PHISH_VAL


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
    # number of categories on x axis
    N = max(len(phishData.keys()), len(nonPhishData.keys()))
    tP = sum(phishData.values())  # total of Phishing Emails
    tNP = sum(nonPhishData.values())  # total of non-Phishing Emails
    # Gets the percentage of each category
    valuePH = [data/tP*100 for data in phishData.values()]
    valueNPH = [data/tNP*100 for data in nonPhishData.values()]

    ind = np.arange(N)
    width = 0.35
    pyplot.ylim(0, 100)
    pyplot.bar(ind, valuePH, width, label='Phishing')
    pyplot.bar(ind+width, valueNPH, width, label='Non-Phishing')
    pyplot.ylabel('Percentage')
    pyplot.title(testName)
    xCategory = list(phishData.keys())
    pyplot.xticks(ind + width / 2, xCategory)
    pyplot.legend(loc='best')
    pyplot.show()


def graphNumerical(phishingResults: list, nonPhishingResults: list, testName="", labelPhishingAxis=False):
    """ Graphs numerical results for each of the categories.

    There are multiple ways to represent this data but for now we use a histogram
    labelPhishingAxis: whether to indicate PHISHING_VALUE and NON_PHISHING_VALUE on the x axis
    """
    nBins = 20

    pyplot.hist(phishingResults, nBins, alpha=0.5, label="Phishing")
    pyplot.hist(nonPhishingResults, nBins, alpha=0.5,  label="Non-Phishing")

    if labelPhishingAxis:
        pyplot.text(PHISH_VAL, 1, "Phishing\nValue")
        pyplot.text(NON_PHISH_VAL, 1, "Non-Phishing\nValue")

    pyplot.title(testName)
    pyplot.legend()
    pyplot.show()


def graphBestFit(phishingResults: list, nonPhishingResults: list, testName=""):
    """ Use least squares to fit a linear trend to the results.

    Phishing emails are given a score of 1  while legitamate emails are given a score of -1.
    """
    # format for approximating system Ax = b
    matA = phishingResults + nonPhishingResults
    vecB = [PHISH_VAL] * len(phishingResults) + \
        [NON_PHISH_VAL] * len(nonPhishingResults)

    predX, residuals, rank, singulars = lstsq(matA, vecB, rcond=None)
    predResults = np.dot(matA, predX)

    phishPredictions = predResults[:len(phishingResults)]
    nonPhishPredictions = predResults[len(phishingResults):]
    graphNumerical(phishPredictions, nonPhishPredictions,
                   testName="Best Fit: "+testName, labelPhishingAxis=True)


def visualizeTest(test):
    """ Graphs test according to type. 

    Test must be a function that takes a single email as argument and has member
    fields .testType and .testName
    """
    # run tests for all
    phishingResults, nonPhishingResults = runTestOnAll(test)

    # graph according to type
    if test.testType == TestType.categorical:
        graphCategorical(phishingResults, nonPhishingResults, test.testName)

    elif test.testType == TestType.numerical:
        graphNumerical(phishingResults, nonPhishingResults, test.testName)

    elif test.testType == TestType.bestfit:
        graphBestFit(phishingResults, nonPhishingResults, test.testName)


if __name__ == "__main__":
    # run specific tests
    visualizeTest(tests.authDomainSenderBestfit)

    # # run all tests
    # for test in tests.allTests:
    #     visualizeTest(test)
