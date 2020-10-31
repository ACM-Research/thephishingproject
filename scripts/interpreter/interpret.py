""" Module for interpreting and visualizing already parsed data.

Loads data from processed_data/analyzer_script/phishing_analysis.json and non_phishing_analysis.json

When it becomes helpful to view data on an x-y plane (i.e. for regression) phishing emails will be given
a y-value of 1 and non-phishing emails will be given a value of 0.
"""
import json
from os import path
import matplotlib.pyplot as pyplot

import tests
from tests import TestType

# Constants
ROOT =  path.abspath(path.join(path.dirname(__file__),"../.." ))
NON_PHISH_PATH = path.join(ROOT,"processed_data","analyzer_script","non_phishing_analysis.json")
PHISH_PATH = path.join(ROOT,"processed_data","analyzer_script","phishing_analysis.json")
NON_PHISH_VAL = 0
PHISH_VAL = 1

# Load jsons into arrays of emails
phish_emails = []
non_phish_emails = []

with open(PHISH_PATH,"r") as phish_info:
    phish_dict = json.load(phish_info)
    phish_emails = list(phish_dict.values())

with open(NON_PHISH_PATH,"r") as non_phish_info:
    non_phish_dict = json.load(non_phish_info)
    non_phish_emails = list(non_phish_dict.values())

if __name__ == "__main__":
    for test in tests.allTests:
        if test.testType == TestType.categorical:
            # get data
            phishingResults = [test(email) for email in phish_emails]
            nonPhishingResults = [test(email) for email in non_phish_emails]
            allCategories = list(set(phishingResults) | set(nonPhishingResults)) # union of unique category values
            phishData = {}
            nonPhishData = {}
            for category in allCategories:
                # this counting algorithm is inefficient (multiple passes)
                phishData[category] = phishingResults.count(category)
                nonPhishData[category] = nonPhishingResults.count(category)
            #graph
            fig, ax = pyplot.subplots()
            ax.plot(list(phishData.keys()), list(phishData.values()), label = "Phishing")
            ax.plot(list(nonPhishData.keys()), list(nonPhishData.values()), label = "Non-Phishing")
            ax.legend()
            pyplot.show()