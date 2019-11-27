# Twitter Network Polarization Tools
This repository contains scripts to parse raw Twitter data to quantify the level of polarization there is within a given combination of topics.

## Usage
Using the scripts require two steps: 1) setting the relevant parameters via 'params.txt' and 2) running 'polarization_scripts.py'.

### Setting parameters
The params.txt file has the following format:

**FIELD:values**  
TWEET_FOLDER:path to raw tweets in json format  
OUTPUT:folder to store intermediary data from first parsing;folder to store intermediary data from second parsing;name of .pickle output; name of .csv output  
TIME:how many days to use to build the Twitter network;how many days to move the time window by  
SET1:text strings to subset tweets by; text strings separated by commas will be in the same network; text strings separated by semi-colons will be in different networks  
SET2:when not-blank, networks are intersections of set1 texts and set2 texts; leave as blank (i.e. SET2:)when only subsetting by one set of text strings

### Running script
The required libraries can be found in the 'tweet_polarization.py' file.
