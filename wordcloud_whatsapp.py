import configparser
import json
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import numpy as npy
from PIL import Image
import re
import string
from collections import Counter

config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

words = config['WORDS']
images = config['IMAGES']

rem_top_words = int(words['rem_top_words'])
keep_words = json.loads(words.get('keep_words'))
ignored_words = json.loads(words.get('ignored_words'))
input_file = words.get('input_file')
background_image = images.get('background_image')
output_image = images.get('output_image')

def create_word_cloud(string):
    maskArray = npy.array(Image.open(background_image))
    cloud = WordCloud(background_color = 'black', max_words = 200, mask = maskArray, stopwords = set(STOPWORDS))
    cloud.generate(string)
    cloud.to_file(output_image)

def word_count(string):
    counts = dict()
    words = string.split()
    for word in words:
        if word in counts:
            counts[word] += 1
        else:
            counts[word] = 1
    return counts

def most_common_words(words, word_count, keep_words):
    top_words = []
    [words.pop(key) for key in keep_words]
    k = Counter(words)
    highest = k.most_common(word_count)
    for i in highest:
        top_words.append(i[0])
    return top_words

with open(input_file, 'r', encoding='utf-8') as f:
    dataset = f.readlines()

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)

new_dataset = []

# CLEAN DATASET
for line in dataset:
    # Remove timestamp with names
    line = re.sub('([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}, ([0-1][0-9]|(2)[0-3]):([0-5][0-9]).*: ', '', line)
    # Remove URLs
    line = re.sub('http\S+', '', line)
    # Remove omitted media entries
    line = re.sub('<Media omitted>', '', line)
    # Remove punctuations (special characers)
    line = line.translate(str.maketrans('', '', string.punctuation))
    # Remove emoticons etc.
    line = emoji_pattern.sub(r'', line)
    # Remove unnecessary whitespace
    line = re.sub(' +', ' ', line)
    line = line.strip()
    # ... and some more cleanup
    line = line.lower()
    new_dataset.append(line)

new_dataset = list(filter(None, new_dataset))

ignored_words.extend(most_common_words(word_count(" ".join(new_dataset)), rem_top_words, keep_words))

ignored_words = set(ignored_words)

print("Ignoring the following words: " + ', '.join(ignored_words))

new_dataset = [" ".join([w for w in t.split() if not w in ignored_words]) for t in new_dataset]

cleaned_dataset = (" ".join(new_dataset))

create_word_cloud(cleaned_dataset)
