import pprint
import itertools
import re
import pke
import string
from nltk.corpus import stopwords
from summarizer import Summarizer
import spacy

spacy.load("en")


def get_summarized_text(full_text):
    model = Summarizer()
    result = model(full_text, min_length=60, max_length=500, ratio=0.4)
    summarized_text = ''.join(result)
    return summarized_text


def get_nouns_multipartite(text):
    out = []

    extractor = pke.unsupervised.MultipartiteRank()
    extractor.load_document(input=text)
    #    not contain punctuation marks or stopwords as candidates.
    pos = {'PROPN', 'NOUN'}
    # pos = {'VERB', 'ADJ', 'NOUN'}
    stoplist = list(string.punctuation)
    stoplist += ['-lrb-', '-rrb-', '-lcb-', '-rcb-', '-lsb-', '-rsb-']
    stoplist += stopwords.words('english')
    extractor.candidate_selection(pos=pos, stoplist=stoplist)
    # 4. build the Multipartite graph and rank candidates using random walk,
    #    alpha controls the weight adjustment mechanism, see TopicRank for
    #    threshold/method parameters.
    extractor.candidate_weighting(alpha=1.1,
                                  threshold=0.75,
                                  method='average')
    keyphrases = extractor.get_n_best(n=5)
    for key in keyphrases:
        out.append(key[0])
    return out


# summarized_text = get_summarized_text(full_text)
summarized_text = ""


def set_summarized_text(full_text):
    global summarized_text
    summarized_text = get_summarized_text(full_text)


def get_filtered_keys(full_text):
    keywords = get_nouns_multipartite(full_text)
    print(keywords)
    filtered_keys = []
    for keyword in keywords:
        if keyword.lower() in summarized_text.lower():
            filtered_keys.append(keyword)

    print(filtered_keys)
    return filtered_keys


# filtered_keys = get_filtered_keys(full_text)


from nltk.tokenize import sent_tokenize
from flashtext import KeywordProcessor


def tokenize_sentences(text):
    sentences = [sent_tokenize(text)]
    sentences = [y for x in sentences for y in x]
    # Remove any short sentences less than 20 letters.
    sentences = [sentence.strip() for sentence in sentences if len(sentence) > 20]
    return sentences


def get_sentences_for_keyword(keywords, sentences):
    keyword_processor = KeywordProcessor()
    keyword_sentences = {}
    for word in keywords:
        keyword_sentences[word] = []
        keyword_processor.add_keyword(word)
    for sentence in sentences:
        keywords_found = keyword_processor.extract_keywords(sentence)
        for key in keywords_found:
            keyword_sentences[key].append(sentence)
            for key in keyword_sentences.keys():
                values = keyword_sentences[key]
                values = sorted(values, key=len, reverse=True)
                keyword_sentences[key] = values
    return keyword_sentences


def get_keyword_sentence_mapping(full_text: str):
    sentences = tokenize_sentences(summarized_text)
    keyword_sentence_mapping = get_sentences_for_keyword(get_filtered_keys(full_text), sentences)

    print(keyword_sentence_mapping)
    return keyword_sentence_mapping


import requests
import json
import re
import random
from pywsd.similarity import max_similarity
from pywsd.lesk import adapted_lesk
from pywsd.lesk import simple_lesk
from pywsd.lesk import cosine_lesk
from nltk.corpus import wordnet as wn


# Distractors from Wordnet
def get_distractors_wordnet(syn, word):
    distractors = []
    word = word.lower()
    orig_word = word
    if len(word.split()) > 0:
        word = word.replace(" ", "_")
    hypernym = syn.hypernyms()
    if len(hypernym) == 0:
        return distractors
    for item in hypernym[0].hyponyms():
        name = item.lemmas()[0].name()
        # print ("name ",name, " word",orig_word)
        if name == orig_word:
            continue
        name = name.replace("_", " ")
        name = " ".join(w.capitalize() for w in name.split())
        if name is not None and name not in distractors:
            distractors.append(name)
    return distractors


def get_wordsense(sent, word):
    word = word.lower()

    if len(word.split()) > 0:
        word = word.replace(" ", "_")

    synsets = wn.synsets(word, 'n')
    if synsets:
        wup = max_similarity(sent, word, 'wup', pos='n')
        adapted_lesk_output = adapted_lesk(sent, word, pos='n')
        lowest_index = min(synsets.index(wup), synsets.index(adapted_lesk_output))
        return synsets[lowest_index]
    else:
        return None


# Distractors from http://conceptnet.io/
def get_distractors_conceptnet(word):
    word = word.lower()
    original_word = word
    if (len(word.split()) > 0):
        word = word.replace(" ", "_")
    distractor_list = []
    url = "http://api.conceptnet.io/query?node=/c/en/%s/n&rel=/r/PartOf&start=/c/en/%s&limit=5" % (word, word)
    obj = requests.get(url).json()

    for edge in obj['edges']:
        link = edge['end']['term']

        url2 = "http://api.conceptnet.io/query?node=%s&rel=/r/PartOf&end=%s&limit=10" % (link, link)
        obj2 = requests.get(url2).json()
        for edge in obj2['edges']:
            word2 = edge['start']['label']
            if word2 not in distractor_list and original_word.lower() not in word2.lower():
                distractor_list.append(word2)

    return distractor_list


def get_questions(full_text: str):
    set_summarized_text(full_text)
    ques = []

    key_distractor_list = {}
    keyword_sentence_mapping = get_keyword_sentence_mapping(full_text)

    for keyword in keyword_sentence_mapping:
        wordsense = get_wordsense(keyword_sentence_mapping[keyword][0], keyword)
        if wordsense:
            distractors = get_distractors_wordnet(wordsense, keyword)
            if len(distractors) == 0:
                distractors = get_distractors_conceptnet(keyword)
            if len(distractors) != 0:
                key_distractor_list[keyword] = distractors
        else:

            distractors = get_distractors_conceptnet(keyword)
            if len(distractors) != 0:
                key_distractor_list[keyword] = distractors

    index = 1
    # print("#############################################################################")
    # print(
    #     "NOTE::::::::  Since the algorithm might have errors along the way, wrong answer choices generated might not be correct for some questions. ")
    # print("#############################################################################\n\n")
    for each in key_distractor_list:
        sentence = keyword_sentence_mapping[each][0]
        pattern = re.compile(each, re.IGNORECASE)
        output = pattern.sub(" _______ ", sentence)

        # print("%s)" % (index), output)
        choices = [each.capitalize()] + key_distractor_list[each]
        temp = []
        temp.append(output)
        temp.append(choices[0])
        top6choices = choices[:6]
        random.shuffle(top6choices)
        temp.append(top6choices)
        temp.append(choices[4:])
        # optionchoices = ['a', 'b', 'c', 'd']
        # for idx, choice in enumerate(top4choices):
        #     print("\t", optionchoices[idx], ")", " ", choice)
        # print("\nMore options: ", choices[4:20], "\n\n")
        # index = index + 1
        ques.append(temp)
    return ques


full_text = "It is uncertain if time travel to the past is physically possible. Forward time travel, outside the usual sense of the " \
            "perception of time, is an extensively observed phenomenon and well-understood within the framework of " \
            "special relativity and general relativity. However, making one body advance or delay more than a few " \
            "milliseconds compared to another body is not feasible with current technology. As for backward time " \
            "travel, it is possible to find solutions in general relativity that allow for it, such as a rotating " \
            "black hole. Traveling to an arbitrary point in spacetime has very limited support in theoretical " \
            "physics, and is usually connected only with quantum mechanics or wormholes."

print(get_questions(full_text))
