Parser
= 

Example parser using mail-parser, beautifulsoup4, textblob. Automatically scans the current directory and extracts information about the email.  

## How to run  
Assuming `python` points to Python 3.x:  
```sh
python -m pip install -r requirements.txt
python parse.py
```

## Options
Read `*.eml` files from another directory
```sh
python parse.py [directory]
```

Redirecting output to file  
```sh
python parse.py > [outfile]
```