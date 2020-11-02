# Renamer

Renames files in a directory to prevent conflicts.  
Please only rename the files one time. If you need to add files, first move them out to a separate temporary directory, rename them, and then add them in.

## Usage
```sh
python renamer.py [directory] [.extension]
```

## Example Usage
```sh
python renamer.py ../../raw_data/eml_files/something .eml
```