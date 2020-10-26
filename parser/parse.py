import os
import sys
import re
import json
import mailparser
from bs4 import BeautifulSoup
from textblob import TextBlob
import language_tool_python
import textstat
import nltk

# determine if we want to save the email body text
save_body = True

# make sure we have punkt downloaded
nltk.download('punkt', quiet=True)

def main(dir):
    checker = language_tool_python.LanguageTool('en-US')

    emails = {}

    for filename in os.listdir(dir):
        if not filename.endswith('.eml'):
            continue
        
        # print to stderr to support output redirection
        print('[INFO] Processing {}...'.format(filename), file=sys.stderr)

        with open(os.path.join(dir, filename), 'r') as file:
            emails[filename] = {}
            mail = mailparser.parse_from_file_obj(file)
            body = BeautifulSoup(mail.body, 'lxml').text.replace(u'\xa0', ' ')
            blob = TextBlob(body)
            grammarErrors = checker.check(body)

            emails[filename] = {
                'subject': mail.subject,
                'from': mail.from_[0][1],
                'to': [tup[1] for tup in mail.to],
                'attachments': [x['filename'] for x in mail.attachments],
                'grammarErrors': len(grammarErrors),
                'counts': {
                    'characterCount': len(body),
                    'wordCount': textstat.lexicon_count(body),
                    'sentenceCount': textstat.sentence_count(body)
                },
                'readability': {
                    'flesch_kincaid': textstat.flesch_kincaid_grade(body),
                    'gunning_fog': textstat.gunning_fog(body),
                    'smog_index': textstat.smog_index(body),
                    'automated_readability_index': textstat.automated_readability_index(body),
                    'coleman_liau_index': textstat.coleman_liau_index(body),
                    'linsear_write': textstat.linsear_write_formula(body),
                },
                'sentiment': {
                    'polarity': blob.sentiment.polarity,
                    'subjectivity': blob.sentiment.subjectivity
                }
            }

            if save_body:
                emails[filename]['body'] = body

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