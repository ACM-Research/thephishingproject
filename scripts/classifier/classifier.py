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


def non_phishing_word_score(email: dict) -> int:
    wordsToCheck = ['information', 'event', 'learn', 'virtual', 'engineering', 'session', 'research', 'announcement']
    weights = [ 9.226401698245681, 19.388451383424893, 21.053712649415615, 9.655421494134131, 16.05580229104695, 9.661801715561216, 6.3515824535352685, 2.7974906560254773]
    # cutoff of 1.2 for whitelisting
    wordCount = 1+email['counts']['wordCount']
    return sum([email['body'].lower().count(word)/wordCount*weights[i] for i, word in enumerate(wordsToCheck)])

def phishing_word_score(email: dict) -> int:
    wordsToCheck = ['work', 'full name', 'arrival', 'service', 'purchase', 'paid', 'phone', 'employ', '$', 'pay', 'paid']
    weights = [0, 0, 0, 0, 25.5, 16.6, 12.4, 20.6, 26.2, 0, 0]
    # cutoff of 1.3
    wordCount = 1+email['counts']['wordCount']
    return sum([email['body'].lower().count(word)/wordCount*weights[i] for i, word in enumerate(wordsToCheck)])

def getXScore(email: dict) -> int:
    return phishing_word_score(email) - non_phishing_word_score(email)

# 0 if school, 1 if personal, 2 if unknown
def getYScore(email: dict) -> int:
    sender_email: str = email['from'].lower()
    personal_emails = ['hotmail', 'gmail', 'yahoo', 'aol', 'msn', 'icloud']
    school_emails = ['utdallas.edu']
    for email_service in school_emails:
        if email_service in sender_email: return 0
    for email_service in personal_emails:
        if email_service in sender_email: return 1
    return 2

#def zFunct(email):
#    wordCount = 1+email['counts']['wordCount']
#    return email['grammarErrors']/wordCount
def getZScore(email):
    # set to 0, 1, or 2 depending on whether or not the from and reply_to fields match
    # 0: unspecified reply to
    # 1: explicit reply to sender
    # 2: explicit reply to a non-sender
    if not email['replyTo']:
        return 0
    elif email['from'] in email['replyTo']:
        return 1
    else:
        return 2

# returns false for non phishing, true for phishing
def classifyPoint(x: int, y: int, z: int) -> bool:
    if z == 0:
        #if y > 0.2 + x: return True
        #else: return False
        if y == 0 or y == 2:
            return x > 0.2
        else:
            return x > -0.1
    elif z == 1:
        return False
    else:
        #if y > 0.2 + x: return True
        #else: return False
        if y == 0 or y == 2:
            return x > 0.2
        else:
            return x > -0.1

# returns tuple of (non phishing, phishing)
def classifySeries(points: dict) -> tuple:
    _phishing = {
        'x': [], 'y': [], 'z': []
    }
    _non_phishing = {
        'x': [], 'y': [], 'z': []
    }
    for i in range(len(points['x'])):
        x, y, z = points['x'][i], points['y'][i], points['z'][i]
        if classifyPoint(x, y, z):
            _phishing['x'].append(x)
            _phishing['y'].append(y)
            _phishing['z'].append(z)
        else:
            _non_phishing['x'].append(x)
            _non_phishing['y'].append(y)
            _non_phishing['z'].append(z)

    return (_non_phishing, _phishing)


# calculate scores
phishing_scores = {
    'x': [getXScore(x) for x in phish_emails],
    'y': [getYScore(x) for x in phish_emails],
    'z': [getZScore(x) for x in phish_emails],
}
non_phishing_scores = {
    'x': [getXScore(x) for x in non_phish_emails],
    'y': [getYScore(x) for x in non_phish_emails],
    'z': [getZScore(x) for x in non_phish_emails],
}

# now, we classify them
false_negative, true_positive = classifySeries(phishing_scores)
true_negative, false_positive = classifySeries(non_phishing_scores)

print(false_negative)
print('Number of false negatives (uncaught spam) out of total spam: {}/{} = {:.2f}%'.format(len(false_negative['x']), len(phishing_scores['x']), 100*len(false_negative['x'])/len(phishing_scores['x'])))
print('Number of false positives (real emails marked as spam): {}/{} = {:.2f}%'.format(len(false_positive['x']), len(non_phishing_scores['x']), 100*len(false_positive['x'])/len(non_phishing_scores['x'])))

fig = go.Figure()

fig.add_trace(go.Scatter3d(
    name='True Positive ({})'.format(len(true_positive['x'])),
    x=true_positive['x'],
    y=true_positive['y'],
    z=true_positive['z'],
    mode='markers',
    marker = {
        'size': 5,
        'color': 'coral',
        'line': {
            'color': 'MediumPurple',
            'width': 1
        }
    }
))
fig.add_trace(go.Scatter3d(
    name='True Negative ({})'.format(len(true_negative['x'])),
    x=true_negative['x'],
    y=true_negative['y'],
    z=true_negative['z'],
    mode='markers',
    marker = {
        'size': 5,
        'color': 'darkgray',
        'line': {
            'color': 'MediumPurple',
            'width': 1
        }
    }
))
fig.add_trace(go.Scatter3d(
    name='False Positive ({})'.format(len(false_positive['x'])),
    x=false_positive['x'],
    y=false_positive['y'],
    z=false_positive['z'],
    mode='markers',
    marker = {
        'size': 5,
        'color': 'darkred',
        'line': {
            'color': 'MediumPurple',
            'width': 1
        }
    }
))
fig.add_trace(go.Scatter3d(
    name='False Negative ({})'.format(len(false_negative['x'])),
    x=false_negative['x'],
    y=false_negative['y'],
    z=false_negative['z'],
    mode='markers',
    marker = {
        'size': 5,
        'color': 'crimson',
        'line': {
            'color': 'MediumPurple',
            'width': 1
        }
    }
))

axisConfig = {
    'showgrid': True,
    'gridcolor': 'black'  
}

fig.update_layout(
    scene = {
        'xaxis': axisConfig,
        'yaxis': axisConfig,
        'zaxis': axisConfig,
    }
)

fig.show()