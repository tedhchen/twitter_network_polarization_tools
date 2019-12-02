# Twitter Network Polarization Tools
This repository contains scripts to parse raw Twitter data to quantify the level of polarization there is within a given combination of topics.

## Usage
Using the scripts require two steps: 1) setting the relevant parameters via `params.txt` and 2) running `polarization_scripts.py`.

### Setting parameters
`params.txt` has the following format:

**FIELD:values**  
TWEET_FOLDER:path to raw tweets in json format  
OUTPUT:folder to store intermediary data from first parsing;folder to store intermediary data from second parsing;name of .pickle output; name of .csv output  
TIME:how many days to use to build the Twitter network;how many days to move the time window by  
SET1:text strings to subset tweets by; text strings separated by commas will be in the same network; text strings separated by semi-colons will be in different networks  
SET2:when not-blank, networks are intersections of set1 texts and set2 texts; leave as blank (i.e. SET2:)when only subsetting by one set of text strings

### Running script
Run the script `polarization_scripts.py`. The required libraries can be found in `tweet_polarization.py`. The script outputs two files: a .pickle file with a nested list `Gs` and a .csv file where rows are networks.

#### Gs.pickle
The `Gs` object is a nested list with the following format:

```
Gs[topic][0][time period][0: networkx graph; 1: [giant component ratio, number of nodes, number of edges]; 2: fr-layout (by default not run); 3: vector of partition membership; 4: random-walk score; 5: objval (see nxmetis.partition)]
```

The networkx graph object `G` has two node attributes: 1) node id (which should be Twitter id if the raw data format is not changed); and 2) partition membership (as one of two colour hex codes).

#### .csv
The output .csv file has the following columns:

```
a) id; b) topic; c) period id; d) text or hashtag (by default networks are subset by text strings); e) number of nodes; f) number of edges; g) giant component ratio; h) 1000 random-walk scores
```
