import os
import sys
import re
import json
import mailparser
from bs4 import BeautifulSoup
from textblob import TextBlob
import language_tool_python
import nltk

# make sure we have punkt downloaded
nltk.download('punkt', quiet=True)

def main(dir):
    checker = language_tool_python.LanguageTool('en-US')

    emails = {}

    for filename in os.listdir(dir):
        if not filename.endswith('.eml'):
            continue
        with open(filename, 'r') as file:
            emails[filename] = {}
            mail = mailparser.parse_from_file_obj(file)
            body = BeautifulSoup(mail.body, 'lxml').text
            blob = TextBlob(body)
            grammarErrors = checker.check(body)

            emails[filename] = {
                'subject': mail.subject,
                'from': mail.from_[0][1],
                'to': [tup[1] for tup in mail.to],
                'attachments': mail.attachments,
                'body': body,
                'grammarErrors': len(grammarErrors),
                'characterCount': len(body),
                'wordCount': len(blob.words),
                'sentenceCount': len(blob.sentences),
                'sentiment': {
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                }
            }

    print(
        json.dumps(emails, indent=2)
    )

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # allow explicit path *.eml files
        main(sys.argv[1])
    else:
        # default to cwd
        main(os.getcwd())