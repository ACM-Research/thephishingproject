# For info: see README.md
import json
from os import path
import plotly.graph_objects as go
import numpy
from numpy.linalg import lstsq

# Constants
ROOT = path.abspath(path.join(path.dirname(__file__), "../.."))
NON_PHISH_PATH = path.join(ROOT, "processed_data",
                           "analyzer_script", "non_phishing_analysis.json")
PHISH_PATH = path.join(ROOT, "processed_data",
                       "analyzer_script", "phishing_analysis.json")

# Load jsons into arrays of emails
phish_emails = []
non_phish_emails = []

with open(PHISH_PATH, "r") as phish_info:
    phish_dict = json.load(phish_info)
    phish_emails = list(phish_dict.values())

with open(NON_PHISH_PATH, "r") as non_phish_info:
    non_phish_dict = json.load(non_phish_info)
    non_phish_emails = list(non_phish_dict.values())


def xFunct(email):
    wordsToCheck = ['information', 'event', 'learn', 'virtual', 'engineering', 'session', 'research', 'announcement']
    weights = [ 9.226401698245681, 19.388451383424893, 21.053712649415615, 9.655421494134131, 16.05580229104695, 9.661801715561216, 6.3515824535352685, 2.7974906560254773]
    # cutoff of 1.2 for whitelisting
    wordCount = 1+email["counts"]["wordCount"]
    return sum([email['body'].lower().count(word)/wordCount*weights[i] for i, word in enumerate(wordsToCheck)])

def yFunct(email):
    wordsToCheck = ['work', 'full name', 'arrival', 'service', 'purchase', 'paid', 'phone', 'employ', '$', 'pay', 'paid']
    weights = [0, 0, 0, 0, 25.5, 16.6, 12.4, 20.6, 26.2, 0, 0]
    # cutoff of 1.3
    wordCount = 1+email["counts"]["wordCount"]
    return sum([email['body'].lower().count(word)/wordCount*weights[i] for i, word in enumerate(wordsToCheck)])

#def zFunct(email):
#    wordCount = 1+email["counts"]["wordCount"]
#    return email['grammarErrors']/wordCount
def zFunct(email):
    # set to 0, 1, or 2 depending on whether or not the from and reply_to fields match
    # 0: unspecified reply to
    # 1: explicit reply to sender
    # 2: explicit reply to a non-sender
    if not email['replyTo']:
        return 0
    elif email["from"] in email["replyTo"]:
        return 1
    else:
        return 2

phishing = {
    'x': [xFunct(x) for x in phish_emails],
    'y': [yFunct(x) for x in phish_emails],
    'z': [zFunct(x) for x in phish_emails],
}
non_phishing = {
    'x': [xFunct(x) for x in non_phish_emails],
    'y': [yFunct(x) for x in non_phish_emails],
    'z': [zFunct(x) for x in non_phish_emails],
}



fig = go.Figure(
    data=[go.Scatter3d(
        x=phishing['x'] + non_phishing['x'],
        y=phishing['y'] + non_phishing['y'],
        z=phishing['z'] + non_phishing['z'],
        mode='markers',
        marker = {
            'size': 5,
            'colorscale': ['coral', 'darkgray'],
            'color': [0]*len(phishing['x']) + [1]*len(non_phishing['x']),
            'line': {
                'color': 'MediumPurple',
                'width': 1
            }
        }
    )
])

fig.show()