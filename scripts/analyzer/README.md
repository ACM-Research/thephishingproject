Analyzer
= 

Example analyzer using mail-parser, beautifulsoup4, textblob. Automatically scans the current directory and extracts information about the email.  

## How to run  
Assuming `python` points to Python 3.x:  
```sh
python -m pip install -r requirements.txt
python analyze.py [directory]
```

This script will read all .eml files in the specified directory and create `analysis.json` and `analysis.csv` in that directory.  
If no directory is specified, the current working directory will be used.  