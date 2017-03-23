# Spamfilter
*Machine learning for filtering out spam in the ENRON spam dataset*
This repository contains sample code for analyzing common words in spam and ham (non-spam) dataset, based on which a classifier can be trained. 

The preprocessing folder containts three scripts.

1. [find_features.py](preprocessing/find_features.py)
	- This script is used to find words that occur frequently in either ham or spam messages, such words are diagnostic. Note that these words are tokenized representations that result from parsing the email body with [spambayes](https://sourceforge.net/p/spambayes/code/HEAD/tree/). It will recursively parse files (under subdirectories of) both the spam and ham subdirectories from the specified input folder, ignoring files with .gz or .tar extension. It expects emails to be availalble in raw txt format.
	```
	usage: find_features.py [-h] [-i INPUT_FOLDER] [-o WORDS] [-n DIFF]

	Match predefined parameters for creating features from text data

	optional arguments:
	  -h, --help            show this help message and exit
	  -i INPUT_FOLDER, --input_folder INPUT_FOLDER
				input folder, with subfolders for spam and ham
	  -o WORDS, --words WORDS
				output list of top words that have differential occurence in
				SPAM vs HAM
	  -n DIFF, --diff DIFF  number of diff words to include
	```
	
2. [match_attributes.py](preprocessing/match_attributes.py)
	- This script parses e-mails from both ham and spam subfolder and creates an entry for every email with values for the features based on the [keyword list](words.txt) derived from find_features.py as well as some other features inspired by the [spambase](https://archive.ics.uci.edu/ml/datasets/Spambase) dataset:
	```
	6 continuous real [0,100] attributes of type char_freq_CHAR] 
	= percentage of characters in the e-mail that match CHAR, i.e. 100 * (number of CHAR occurences) / total characters in e-mail 

	1 continuous real [1,...] attribute of type capital_run_length_average 
	= average length of uninterrupted sequences of capital letters 

	1 continuous integer [1,...] attribute of type capital_run_length_longest 
	= length of longest uninterrupted sequence of capital letters 

	1 continuous integer [1,...] attribute of type capital_run_length_total 
	= sum of length of uninterrupted sequences of capital letters 
	= total number of capital letters in the e-mail 
	``` 
	The output is a tab separated file with an entry for every email. The feature "spam" is 1 for spam emails and 0 for ham emails. It calculates the relative frequency of the words that w
3. [preprocessing.py](preprocessing/preprocessing.py)
