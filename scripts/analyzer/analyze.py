import os
import sys
import re
import json
import mailparser
from textblob import TextBlob
import language_tool_python
import textstat
import nltk
from bs4 import BeautifulSoup
import cv2
import gif2numpy
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO
import base64
import chardet

# determine if we want to save the email body text
save_body = True

# make sure we have punkt downloaded
nltk.download('punkt', quiet=True)



def main(dir: str):
    checker = language_tool_python.LanguageTool('en-US')
    emails = {}

    filenames = [filename for filename in os.listdir(dir) if filename.endswith('.eml')]
    for filename in filenames:
                
        print()
        print('[INFO] Processing {}...'.format(filename))

        with open(os.path.join(dir, filename), 'r', encoding='latin1') as file:
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
            # if 'Authentication-Results' not in mail.headers:
            #     print('[WARNING] This email is missing an authentication results header! Skipping...')
            #     continue

            attachments = ''
            try:
                mail.write_attachments(dir)
                for attachment in mail.attachments:
                    if re.search('image', attachment['mail_content_type']):
                        if re.search('gif', attachment['mail_content_type']):
                            images, _, _ = gif2numpy.convert(dir + '\\' + attachment['filename'])
                            img = images[0]
                        else:
                            img = cv2.imread(dir + '\\' + attachment['filename'])
                        img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
                        text = pytesseract.image_to_string(img)
                        attachments += text
                    elif re.search('pdf', attachment['mail_content_type']):
                        encoding = chardet.detect(pdf_to_text(dir + '\\' + attachment['filename']))['encoding']
                        attachments += pdf_to_text(dir + '\\' + attachment['filename']).decode(encoding)
                    elif re.search('text', attachment['mail_content_type']):
                        encoding = chardet.detect(base64.b64decode(attachment['payload']))['encoding']
                        attachments += base64.b64decode(attachment['payload']).decode(encoding)
                    else:
                        attachments += attachment['payload']
                    os.remove(dir + '\\' + attachment['filename'])
            except Exception as e:
                print('[WARNING] Error with attachments: {}'.format(e))
            body = remove_noise(BeautifulSoup(mail.body, 'lxml').get_text(separator=' ', strip=True) + BeautifulSoup(attachments, 'lxml').get_text())
            if len(body) == 0:
                print('zero', body)
            #print(body)
            blob = TextBlob(body)
            grammarErrors = checker.check(body)

            if 'Authentication-Results' in mail.headers:
                spf = re.findall('spf=(\S*)', mail.headers['Authentication-Results'])
                dkim = re.findall('dkim=(\S*)', mail.headers['Authentication-Results'])
                dmarc = re.findall('dmarc=(\S*)', mail.headers['Authentication-Results'])
            else:
                spf = dkim = dmarc = ''

            emails[filename] = {
                'filename': filename,
                # 'hops': mail.received[-1]['hop'],
                # 'totalDelay': sum([hop['delay']/60 for hop in mail.received]),
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
    # if not emails:
    #     print('[WARNING] No files were found in "{}"!'.format(dir))
    #     return

    ## output json ##
    with open(os.path.join(dir, 'analysis.json'), 'w') as jsonFile:
        json.dump(emails, jsonFile, indent=2)

    ## build and output csv ##

    # generate and output headers using first email
    column_headers = list(flatten_json(emails[list(emails.keys())[0]]).keys())
    csvFile = open(os.path.join(dir, 'analysis.csv'), 'w', encoding='utf-8')
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

def remove_noise(text):
    cleaned_tokens = []
    for line in text.split():
        if line == '' or re.search(r'www\..*\....', line) is not None or \
                line == '\xA9':
            continue
        if line == 'mail_boundary':
            cleaned_tokens.pop()
            break
        line = re.sub(r'\(|\)|:|,|\||"|\?|_|/|\[|]|-{2,}', '', line) # replace punctuation with space
        cleaned_tokens.append(line)

    # body = re.sub('www\..*\....', '', text) # delete links
    # body = re.sub('https?:\/\/[^\/]*\/.*$', ' ', body, flags=re.MULTILINE) # delete links
    # body = re.sub(r'[!,?."]', ' ', body) # punctuation replacement v0.1
    # body = re.sub('--- mail_boundary ---.*', '', text) # remove everything after mail boundary
    return ' '.join(cleaned_tokens)

def pdf_to_text(path):
    manager = PDFResourceManager()
    retstr = BytesIO()
    layout = LAParams(all_texts=True)
    device = TextConverter(manager, retstr, laparams=layout)
    filepath = open(path, 'rb')
    interpreter = PDFPageInterpreter(manager, device)

    for page in PDFPage.get_pages(filepath, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    filepath.close()
    device.close()
    retstr.close()
    return text

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
