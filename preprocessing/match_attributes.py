#!/usr/bin/env python
"""Match attributes"""
import sys
import re
import os
import argparse
import email.parser
#spambayes contains a usefull tokenizer for recognizing email text
from spambayes import tokenizer
tok = tokenizer.Tokenizer()
# import hunspell
# import nltk
# hobj = hunspell.HunSpell('/Library/Spelling/en_US.dic','/Library/Spelling/en_US.aff' )

# """"""
#Features inspired by spambase.
# 6 continuous real [0,100] attributes of type char_freq_CHAR
# = percentage of characters in the e-mail that match CHAR,
# i.e. 100 * (number of CHAR occurences) / total characters in e-mail
#
# 1 continuous real [1,...] attribute of type capital_run_length_average
# = average length of uninterrupted sequences of capital letters
#
# 1 continuous integer [1,...] attribute of type capital_run_length_longest
# = length of longest uninterrupted sequence of capital letters
#
# 1 continuous integer [1,...] attribute of type capital_run_length_total
# = sum of length of uninterrupted sequences of capital letters
# = total number of capital letters in the e-mail
#
# 1 nominal {0,1} class attribute of type spam
# = denotes whether the e-mail was considered spam (1) or not (0),
# i.e. unsolicited commercial e-mail.
#

def parse_args():
    "Pass command line arguments"
    # if not sys.argv[1:]:
    #     sys.argv.append('-h')
    parser = argparse.ArgumentParser(description='Match predefined parameters for creating features from text data')
    parser.add_argument('-c','--characters',
                        help='Characters to match, list of characters from txt file',
                        default='/Users/thomasvangurp/PycharmProjects/spam_ham_bigdatarepublic/char_freq.txt')
    parser.add_argument('-w','--words',
                        help='words to match, list of words from txt file',
                        #default='/Users/thomasvangurp/enron-spam/words.txt')
                        default='/Users/thomasvangurp/PycharmProjects/spam_ham_bigdatarepublic/word_freq.txt')
    parser.add_argument('-i','--input_folder',
                        help='input folder, with subfolders for spam and ham',
                        default='/Users/thomasvangurp/enron-spam')
    parser.add_argument('-o', '--output',
                        help='tab separated output file with features formatted',
                        default='/Users/thomasvangurp/enron-spam/output_100K_spambase_48.tsv')
    args = parser.parse_args()
    return args

def count_char(text,char):
    """count occurence of specific characters in text"""
    char_count = {}
    for c in char:
        char_count[c] = text.count(char)
    return char_count


# def initialize_hunspell_obj(words_to_add):
#     """initialize hunspell object with custom words added if these do not exist..."""
#     if os.path.exists('/Library/Spelling/en_US.dic') and os.path.exists('/Library/Spelling/en_US.aff'):
#         hobj = hunspell.HunSpell('/Library/Spelling/en_US.dic', '/Library/Spelling/en_US.aff')
#     else:
#         #TODO: find automatic way for locating dictionaries
#         #TODO: let user specify for which languages to check words
#         raise OSError("en_US.dic and en_US.aff not found, please change path in script")
#     for word in words_to_add:
#         if not hobj.spell(word):
#             hobj.add(word)
#     return hobj


# def clean_word(input_list, hunspell_obj):
#     """Clean misspelled words"""
#     output_list = []
#     #https: // github.com / blatinier / pyhunspell
#     #TODO: return number and ratio of misspelled words
#     mistakes = 0
#     correct = 0
#     for word in input_list:
#         if len(word) == 1 and not word[0].isalpha():
#             continue
#         if hunspell_obj.spell(word):
#             #make sure we remove all non alpha-mumeric chars
#             word = re.sub(r'[^a-zA-Z0-9]', '', word)
#             output_list.append(word)
#             correct += 1
#         else:
#             #TODO: analyze if we do not need to assess word further..
#             try:
#                 output_list.append(hunspell_obj.suggest(word)[0])
#             except IndexError:
#                 pass
#             mistakes += 1
#     total = correct + mistakes
#     error_ratio = mistakes / float(total)
#     return output_list, error_ratio

def capital_run_length(text):
    """returns:
     1. the longest string of CAPITALs      =  capital_run_length_longest,
     2. the total length of capital strings =  capital_run_length_total,
     3. the average length of capitals      =  capital_run_length_average
    """
    capital_run_length_longest = 0
    cap_len = 0
    cap_len_list = []
    #loop over characters
    for c in text:
        if c.isalpha() and c.isupper(): #we are only interested in alphabetic characters.
            cap_len += 1
        else:
            if cap_len != 0:
                #we just ended a CAPITAL string, add length to dictionary
                cap_len_list.append(cap_len)
                # if this cap_len is longer than existing max, reset capital_run_length_longest
                if cap_len > capital_run_length_longest:
                    capital_run_length_longest = int(cap_len)
            cap_len = 0
    #total length is sum of all capital strings
    capital_run_length_total = sum(cap_len_list)
    try:
        capital_run_length_average = capital_run_length_total / float(len(cap_len_list))
    except ZeroDivisionError:
        capital_run_length_average = 0

    return capital_run_length_longest, capital_run_length_total, capital_run_length_average


def get_file_list(dir):
    """get a list of all files in a folder and its subfolders"""
    file_out = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            file_path = os.path.join(root, file)
            file_out.append(file_path)
        for dir in dirs:
            sub_dir = os.path.join(root,dir)
            file_out += get_file_list(sub_dir)
    return file_out

def parse_folder(args):
    """parse email messages in folder that has subfolders ham and spam"""
    try:
        input_folder = os.listdir(args.input_folder)
    except OSError:
        raise OSError('%s does not exist' % args.input_folder)
    if 'spam' in input_folder and 'ham' in input_folder:
        spam_folder = os.path.join(args.input_folder,'spam')
        ham_folder = os.path.join(args.input_folder,'ham')
        ham_files = get_file_list(ham_folder)
        spam_files = get_file_list(spam_folder)
    else:
        raise OSError('Subfolder ham or spam is not present in %s' % args.input_folder)
    return spam_files, ham_files

def set_features_search(args):
    """read features to process from files, features can be characters, words or categories"""
    search_features = {'words':[],'chars':[],'CAT':[]}
    #TODO: test 100 most frequently used words in SPAM training set
    with open(args.words) as handle:
        for word in handle:
            if word.startswith('CAT'):
                #category of search string assigned by spambayes tokenizer
                search_features['CAT'].append(word[4:].rstrip('\r').rstrip('\n'))
            else:
                search_features['words'].append(word.rstrip('\n').rstrip('\r'))
    #TODO: evalutate average ASCII distance and stdev http://ascii.cl between characters
    with open(args.characters) as handle:
        for char in handle:
            search_features['chars'].append(char.rstrip('\n').rstrip('\r'))
    return search_features

def parse_email(handle):
    """parse raw email from text and return msg object"""
    parser = email.parser.FeedParser()
    raw_email = handle.read()
    try:
        parser.feed(raw_email)
    except Exception:
        raise Exception('file format not valid')
    msg = parser.close()
    return msg

def get_features(msg, search_features, tok):
    """get features from email message object"""
    features = {}
    email_body = msg._payload
    if email_body == '':
        return 0
    #If the email body contains other message(s), parse the firsr
    if type(email_body[0]) == type(msg):
        email_body = msg._payload[0]._payload
        if type(email_body) != type('a'):
            return 0
        elif email_body == '':
            return 0
    #TODO: find more elegant solution for hard-coded reference to capital_run_length as 'special' feature
    longest_cap, total_cap, avg_cap = capital_run_length(email_body)
    features['longest_cap'] = longest_cap
    features['total_cap'] = total_cap
    features['avg_cap'] = avg_cap
    # except UnicodeDecodeError:
    #     email_body =  ''.join(i for i in email_body if ord(i)<128)
    #     tokenized_words = nltk.word_tokenize(email_body)
    tokenized_words = [word for word in tok.tokenize_body(msg)]
    if len(tokenized_words) <= 1:
        return 0
    #get relative frequency of words to search for
    for search_word in search_features['words']:
        #make sure all strings are lower-case
        features['word_freq_%s' % search_word] = tokenized_words.count(search_word)/\
                                                 float(len(tokenized_words))
    #get relative frequency of characters to search for
    for search_char in search_features['chars']:
        features['char_freq_%s' % search_char] = email_body.count(search_char) / float(len(email_body))
    joined_words = ' '.join(tokenized_words)
    #get relative frequencies of categories (special chars)
    for CAT in search_features['CAT']:
        #make sure all strings are lower-case
        features['CAT_freq_%s' % CAT] = joined_words.count(search_word)/\
                                                 float(len(tokenized_words))
    return features

def main():
    """main function loop"""
    args = parse_args()
    search_features = set_features_search(args)
    spam_files, ham_files = parse_folder(args)
    #TODO: make subsets for training and testing of both ham and SPAM
    #instantiate a hunspell object, search words should be added if they were not yet present
    # hunspell_obj = initialize_hunspell_obj(search_features['words'])
    header_written = False
    out_handle = open(args.output,'w')
    for n,file in enumerate(spam_files):
        if not file.endswith('.gz') or file.endswith('.tar'):
            if n % 2:
                continue
            if not n % 120000 and n > 0:
                break
            handle = open(file)
            email_object = parse_email(handle)
            features = get_features(email_object, search_features, tok)
            if not features:
                n -= 1
                continue
            features['spam'] = 1
            if header_written:
                output = ['%f' % v for k, v in sorted(features.items())]
                out_handle.write('\t'.join(output) + '\n')
            else:
                header = [k for k, v in sorted(features.items())]
                output = ['%f' % v for k, v in sorted(features.items())]
                out_handle.write('\t'.join(header) + '\n')
                out_handle.write('\t'.join(output) + '\n')
                header_written = True
            handle.close()
    for n,file in enumerate(ham_files):
        if not file.endswith('.gz') or file.endswith('.tar'):
            if n % 2:
                continue
            if not n % 120000 and n > 0:
                break
            handle = open(file)
            email_object = parse_email(handle)
            features = get_features(email_object, search_features, tok)
            if not features:
                n -= 1
                continue
            features['spam'] = 0
            if header_written:
                output = ['%f' % v for k, v in sorted(features.items())]
                out_handle.write('\t'.join(output) + '\n')
            else:
                header = [k for k, v in sorted(features.items())]
                output = ['%f' % v for k, v in sorted(features.items())]
                out_handle.write('\t'.join(header) + '\n')
                out_handle.write('\t'.join(output) + '\n')
                header_written = True
            handle.close()
    out_handle.close()


if __name__ == '__main__':
    main()