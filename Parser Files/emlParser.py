import outlookmsgfile
import os
import email

path = input("Enter Path: ")
listing = os.listdir(path)

# This Takes in all .eml and .msg files in the path and prints the headers
for fle in listing:
    if str.lower(fle[-3:]) == "msg":
        eml = outlookmsgfile.load(open(fle))
        msg = email.message_from_string(eml.as_string())
        # Printing email header
        print(msg)
        print()
    if str.lower(fle[-3:]) == "eml":
        eml = outlookmsgfile.load(open(fle))
        msg = email.message_from_string(eml.as_string())
        # Printing email header
        print(msg)
        print()
