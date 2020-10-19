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
            #emails[filename]['sender'] = mail.from_
            emails[filename]['sender'] = mail.from_[0][1]
            emails[filename]['attachments'] = mail.attachments
            #emails[filename]['to'] = mail.to
            emails[filename]['to'] = [tup[1] for tup in mail.to]
            emails[filename]['subject'] = mail.subject
            filtered = BeautifulSoup(mail.body, 'lxml').text
            emails[filename]['body'] = filtered
            b = TextBlob(filtered)
            emails[filename]['sentiment'] = b.sentiment

f = open('output.txt', 'w')
for k, v in emails.items():
    f.writelines(["file:" + k + "\n"])
    for key in v:
        f.writelines( [key + ": " + str(v[key]) + "\n"] )
    f.write("\n")
f.close()
