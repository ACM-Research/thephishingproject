import json
from os import path
import numpy as np
from numpy.linalg import lstsq


# Constants
ROOT = path.abspath(path.join(path.dirname(__file__), "../.."))
NON_PHISH_PATH = path.join(ROOT, "processed_data",
                           "analyzer_script", "non_phishing_analysis.json")
PHISH_PATH = path.join(ROOT, "processed_data",
                       "analyzer_script", "phishing_analysis.json")
NON_PHISH_WORD_PATH = path.join(ROOT, "processed_data",
                                "analyzer_script", "non_phishing_words.txt")
PHISH_WORD_PATH = path.join(ROOT, "processed_data",
                            "analyzer_script", "phishing_words.txt")
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


def runTestOnAll(test):
    """ Runs a test on all datasets and returns (phishingResultList, nonPhishingResultList) tuple """
    return [test(email) for email in phish_emails], [test(email) for email in non_phish_emails]


def findOptimizationVector(test):
    """ Runs linear least squares regression on all email for a given test. Test must be of type bestfit. 

    Returns: predictedX, predictedPhishingValues, predictedNonPhishingValues
    """
    phishResults, nonPhishResults = runTestOnAll(test)
    # format for approximating system Ax = b
    matA = phishResults + nonPhishResults
    vecB = [PHISH_VAL] * len(phishResults) + [NON_PHISH_VAL] * len(nonPhishResults)

    predX, residuals, rank, singulars = lstsq(matA, vecB, rcond=None)

    ### Output optimization result to console for analysis ###

    indices = list(range(len(predX)))
    totalImpact = [sum([abs(predX[i] * row[i]) for row in matA]) for i in indices]

    sortMatrix = list(np.transpose((indices , predX , totalImpact)))
    sortMatrix.sort(key = lambda row: row[2], reverse= True)

    print("Test name: ", test.testName)
    print("Raw prediction vector: ", predX)
    print("Variable Index | Prediction coefficient | Total impact")
    for row in list(sortMatrix):
        print("%14i | %22.5f | %12.2f" % (row[0], row[1], row[2]))
    print()

    ### End output ###

    return predX, np.dot(phishResults, predX), np.dot(nonPhishResults, predX)
