# Spamfilter
*Machine learning for filtering out spam in the [ENRON spam dataset](http://www.aueb.gr/users/ion/data/enronQspam/)*

This repository contains sample code for analyzing common words in spam and ham (non-spam) dataset, based on which a classifier can be trained. 

**Requirements** *(non standard python modules)*:
- Spambayes: https://sourceforge.net/p/spambayes/code/HEAD/tree/
- Scikit-learn and downstream dependencies: pip install scikit-learn (python3.5  or higher) see http://scikit-learn.org/stable/install.html
- Nltk: ```pip install nltk```
- Pandas: ```pip install pandas``` 


The [preprocessing](preprocessing) folder containts two scripts:

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
	- THe type of features that we look for here are inspired by those used in [spambase](https://archive.ics.uci.edu/ml/datasets/Spambase). [Spambayes](https://sourceforge.net/p/spambayes/code/HEAD/tree/) [tokenizer](https://mail.python.org/pipermail/spambayes-checkins/2003-December/002441.html "email entry with the tokenizer code") provides for separation of words and parts of urls that are present in the email body. We look for spambayes tokenized words that have are overrepresented in either spam or ham dataset (highest difference in absolute count). We also add the categories of the special tokens to the word list, prepended by CAT_.

	
2. [match_attributes.py](preprocessing/match_attributes.py)
	- This script parses e-mails from both ham and spam subfolder and creates an entry for every email with values for the features based on the [keyword list](words.txt) derived from find_features.py as well as some other features inspired by the [spambase](https://archive.ics.uci.edu/ml/datasets/Spambase) dataset.
	```
	usage: match_attributes.py [-h] [-c CHARACTERS] [-w WORDS] [-i INPUT_FOLDER]
                           [-o OUTPUT]

	Match predefined parameters for creating features from text data

	optional arguments:
	  -h, --help            show this help message and exit
	  -c CHARACTERS, --characters CHARACTERS
				Characters to match, list of characters from txt file
	  -w WORDS, --words WORDS
				words to match, list of words from txt file
	  -i INPUT_FOLDER, --input_folder INPUT_FOLDER
				input folder, with subfolders for spam and ham
	  -o OUTPUT, --output OUTPUT
				tab separated output file with features formatted
	```
	1. **Words** (float: fraction of tokens / total number of spambayes tokens in email body): based on the tokenized words/entries that result from parsing the email body using the email.parser module using spambayes' tokenizer. “stop” words like the, we, I etc. that occur frequently but have a low information content are excluded. 
	2. **Categories** (float: fraction of tokens with category / total number of spambayes tokens in email body). Spambayes splits the content of the email body into tokens, which are categorized. Examples of such categories are url or skip, which indicate a token is part of a web link or [skip](https://mail.python.org/pipermail/spambayes-checkins/2003-December/002441.html), which indicates how many characters were not parsed. The fraction of entries in the tokenized email body text that is catecgorized as being part of a category is taken on as a separate feature. Certain categorized tokens such as url:aspx and skip:e 10 are also present as words.
	3. **Characters** (float: fraction of char / total number of chars in email body): characters that were used in [spambase](https://archive.ics.uci.edu/ml/datasets/Spambase)
	```
	6 continuous real [0,100] attributes of type char_freq_CHAR] 
	= percentage of characters in the e-mail that match CHAR, i.e. 100 * (number of CHAR occurences) / total characters in e-mail:
	;
	(
	[
	!
	$
	#
	```
	4. **CAPITAL_run_length** related attributes such as defined in spambase:
	```
	1 continuous real [1,...] attribute of type capital_run_length_average 
	= average length of uninterrupted sequences of capital letters 

	1 continuous integer [1,...] attribute of type capital_run_length_longest 
	= length of longest uninterrupted sequence of capital letters 

	1 continuous integer [1,...] attribute of type capital_run_length_total 
	= sum of length of uninterrupted sequences of capital letters 
	= total number of capital letters in the e-mail 
	``` 
	The output is a tab separated file with an entry for every email. The feature "spam" is 1 for spam emails and 0 for ham emails. 

Finally, [email_classifier.py](email_classifier.py) is the main script, with the following parameters:
```
	usage: email_classifier.py [-h] [-c CATEGORY_ID] [-i INPUT] [-s SEPERATOR]
					   [-m MODEL] [-r RATIO] [-o OUTPUT]

		Match predefined parameters for creating features from text data

		optional arguments:
		  -h, --help            show this help message and exit
		  -c CATEGORY_ID, --category_ID CATEGORY_ID
					category ID of the variable that is to be predicted
		  -i INPUT, --input INPUT
					input dataset in comma or tab separated txt
		  -s SEPERATOR, --seperator SEPERATOR
					symbol that separates the entries
		  -m MODEL, --model MODEL
					scikit-learn model to use, see http://scikit-learn.org/stable/
		  -r RATIO, --ratio RATIO
					ratio of input data to use for testing
		  -o OUTPUT, --output OUTPUT
					output directory for writing log file and outputs
```
The classifier script applies machine learning algorithms to train a model to distinguish spam from ham entries from a training subset taken from the tsv file with parameter feature values. The model performance is subsequently evaluated on a separate “test” dataset for which we know the categories, but let the model predict these. Comparing the predicted with the actual category (spam or ham) indicates model performance. Details on the parameters, processing etc. can be found in the comments of [email_classifier.py](email_classifier.py).

