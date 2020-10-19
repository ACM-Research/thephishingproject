import re
import mailparser
from bs4 import BeautifulSoup
import os
from textblob import TextBlob

emails = {}

for filename in os.listdir(os.getcwd()):
    if re.search('.eml$', filename):
        with open(filename, 'r') as file:
            emails[filename] = {}
            mail = mailparser.parse_from_file_obj(open(filename))
            emails[filename]['sender'] = mail.from_
            emails[filename]['attachments'] = mail.attachments
            emails[filename]['to'] = mail.to
            emails[filename]['subject'] = mail.subject
            filtered = BeautifulSoup(mail.body, 'lxml').text
            emails[filename]['body'] = filtered
            b = TextBlob(filtered)
            emails[filename]['sentiment'] = b.sentiment

for k, v in emails.items():
    print("\nfile:", k)
    for key in v:
        print(key + ":", v[key])