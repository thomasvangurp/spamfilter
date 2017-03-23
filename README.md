# Spamfilter
*Machine learning for filtering out spam in the ENRON spam dataset*
This repository contains sample code for analyzing common words in spam and ham (non-spam) dataset, based on which a classifier can be trained. 

The preprocessing folder containts three scripts.

1. [find_features.py](preprocessing/find_features.py)
	- This script is used to find words that occur frequently in either ham or spam messages, such words are diagnostic. Note that these words are tokenized representations that result from parsing the email body with [spambayes](https://sourceforge.net/p/spambayes/code/HEAD/tree/).
	```
	usage: find_features.py [-h] [-i INPUT_FOLDER] [-o WORDS] [-n DIFF]

Match predefined parameters for creating features from text data

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FOLDER, --input_folder INPUT_FOLDER
                        input folder, with subfolders for spam and ham
  -o WORDS, --words WORDS
                        top list of words that have differential occurence in
                        SPAM vs HAM
  -n DIFF, --diff DIFF  number of diff words to include
```
	
2. [match_attributes.py](preprocessing/match_attributes.py)
3. [preprocessing.py](preprocessing/preprocessing.py)
