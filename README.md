# Parsing alternative names from Wikipedia Infoboxes

## Parser
parser.py file is used to parse bz2 file from Wikipesdia dumps. It creates two output files where name and its alternative names from Infoboxes are saved. These files are saved in
Outputs dictionary, too.

## Indexer
indexer.py creates two index directories, one where alternative names for name are saved, and another where names for alternative name is saved. 

## Searching 
search_engine.py is the main file. It provides full text search in parsed alternative names and names.
