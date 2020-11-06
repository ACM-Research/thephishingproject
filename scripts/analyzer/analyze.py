import os
import sys
import re
import json
import mailparser
from textblob import TextBlob
import language_tool_python
import textstat
import nltk

# determine if we want to save the email body text
save_body = False

# make sure we have punkt downloaded
nltk.download('punkt', quiet=True)



def main(dir: str):
    checker = language_tool_python.LanguageTool('en-US')
    emails = {}

    filenames = os.listdir(dir)
    for filename in filenames:
        if not filename.endswith('.eml'):
            continue
                
        print()
        print('[INFO] Processing {}...'.format(filename))

        with open(os.path.join(dir, filename), 'r') as file:
            try:
                mail = mailparser.parse_from_file_obj(file)
            except Exception as e:
                print('[WARNING] Error while parsing: {}'.format(e))
                continue

            # filter duplicates based on subject
            #if mail.subject in emails:
            #    print('[WARNING] This email seems to be a duplicate of "{}"! Skipping...'
            #        .format(emails[mail.subject]['filename']))
            #    continue

            # don't process if auth results missing
            if 'Authentication-Results' not in mail.headers:
                print('[WARNING] This email is missing an authentication results header! Skipping...')
                continue


            #body = re.sub('--- mail_boundary ---.*', ' ', BeautifulSoup(mail.body, 'lxml').text.replace(u'\xa0', ' '), flags=re.DOTALL)
            body = mail.text_plain[0] if mail.text_plain else ''
            blob = TextBlob(body)
            grammarErrors = checker.check(body)

            spf = re.findall('spf=(\S*)', mail.headers['Authentication-Results'])
            dkim = re.findall('dkim=(\S*)', mail.headers['Authentication-Results'])
            dmarc = re.findall('dmarc=(\S*)', mail.headers['Authentication-Results'])


            emails[filename] = {
                'filename': filename,
                'hops': mail.received[-1]['hop'],
                'totalDelay': sum([hop['delay']/60 for hop in mail.received]),
                'spf': spf[0] if len(spf) else None,
                'dkim': dkim[0] if len(dkim) else None,
                'dmarc': dmarc[0] if len(dmarc) else None,
                'subject': mail.subject,
                'from': mail.from_[0][1],
                'to': [tup[1] for tup in mail.to],
                'replyTo': [tup[1] for tup in mail.reply_to],
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

    ## quit if nothing found ##
    if not emails:
        print('[WARNING] No files were found in "{}"!'.format(dir))
        return

    ## output json ##
    with open(os.path.join(dir, 'analysis.json'), 'w') as jsonFile:
        json.dump(emails, jsonFile, indent=2)

    ## build and output csv ##

    # generate and output headers using first email
    column_headers = list(flatten_json(emails[list(emails.keys())[0]]).keys())
    csvFile = open(os.path.join(dir, 'analysis.csv'), 'w')
    csvFile.write(',{}\n'.format(','.join(column_headers)))
    
    # generate and output one line per email
    for email in emails.keys():
        # flatten json to 1 layer deep
        flattened_email = flatten_json(emails[email])
        # generate the values for this row
        csv_values = ['"'+str(flattened_email[column_header])+'"' for column_header in column_headers]
        # add email name and join w/ commas, then write out
        csvFile.write('{},{}\n'.format('"'+email+'"', ','.join(csv_values)))

    csvFile.close()


    # print out stats
    print('{}/{} processed. The remaining failed for some reason.'
        .format(len(emails), len(filenames)))

# flatten json into single layer by concatenating keys with '.'
def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '.')
        elif type(x) is list:
            out[name[:-1]] = ','.join([str(data) for data in x])
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # allow explicit path *.eml files
        main(sys.argv[1])
    else:
        # default to cwd
        main(os.getcwd())
