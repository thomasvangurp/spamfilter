#!/usr/bin/env python
"""Preprocessing of raw email records, implements filtering used by Metsis et al plus additional filterin"""
import os
import email.parser
from htmllaundry import sanitize
from bs4 import BeautifulSoup
from nltk import clean_html,word_tokenize


#parse email, this works
def parse_email(raw_text):
    """parse raw email from text and return msg object"""
    parser = email.parser.FeedParser()
    parser.feed(raw_text)
    msg = parser.close()
    return msg

test_email_handle = open('/Users/thomasvangurp/PycharmProjects/spam_ham_bigdatarepublic/preprocessing/test_email.txt')
raw_text = test_email_handle.read()
msg = parse_email(raw_text)
msg_body = msg._payload
tree = BeautifulSoup(msg_body)
good_html = tree.prettify()
# good_html = clean_html(msg_body)
text = tree.get_text()
output = ''
for c in good_html:
    if c == '<':
        write = False
    elif c == '>':
        write = True
    else:
        if write and c.isalpha:
            output += c.lower()
print output
#test sanitize module
print sanitize(msg_body)

#discard tokens that do not occur in at least 5 messages of the training data!

#test clean_html from nltk
# html_cleaned = clean_html(msg_body)
# text = soup.get_text()
# tokens = word_tokenize(html_cleaned)
# print ''

