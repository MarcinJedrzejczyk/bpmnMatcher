# -*- coding: utf-8 -*-
from __future__ import division
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords, wordnet, wordnet_ic
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.metrics import edit_distance

from wiktionaryparser import WiktionaryParser

import nltk
import networkx as nx
from nltk.wsd import lesk
import math

"""
Functions were made with English strings as input. Characters with diacritic can cause unpredicted behaviour.

"""
stop_words = set(stopwords.words('english'))
semcor_ic = wordnet_ic.ic('ic-semcor.dat')

# there are only word tokens,
tokenizer = RegexpTokenizer(r'\w+')

wiktionary_parser = WiktionaryParser()
wordnet_lemmatizer = WordNetLemmatizer()


# only stop word elimination
def stop_words_elimination(text):
    """
    :param text: List of tokens/strings
    :return: a list of tokens/strings without stopwords
    """
    text_no_stop_words = []
    for word in text:
        if word not in stop_words:
            text_no_stop_words.append(word)
    return text_no_stop_words


def lemminisation(text):
    """

    :param text: string or list of string to lemminizate
    :return: list of input words lemmas(basic word form)
    """

    to_return = []
    if type(text) is list:
        for word in text:
            to_return.append(wordnet_lemmatizer.lemmatize(word))
    else:
        to_return.append(wordnet_lemmatizer.lemmatize(text))
    return to_return


def stemming(text_to_stemm):
    """

    :param text_to_stemm: string or list of string to stemm
    :return: list of stemmed input words
    """
    ps = PorterStemmer()
    to_return = []
    if type(text_to_stemm) is list:
        for word in text_to_stemm:
            to_return.append(ps.stem(word))

    else:
        to_return.append(ps.stem(text_to_stemm))
    return to_return


def get_bag_of_words(textList):
    """
    :param text: list of words
    :return: dictionary words:word_count_in_input
    """
    bag_of_words = {}
    for token in textList:
        bag_of_words[token] = textList.count(token)
    return bag_of_words


def get_tokens(text):
    """
    :param text: String to tokenize
    :return: list of word tokens, alone tokeizer.tokenize() returns from '123,asd?!d' => ['123', 'asd', 'd']
    """
    # return [x for x in tokenizer.tokenize(text) if x.isalpha()]
    return tokenizer.tokenize(text)


def get_tokens_without_stop_words(something):
    """

    :param something: String to tokenize and stop word elimination
    :return: List of Tokens from string without stop words
    """

    return stop_words_elimination(get_tokens(something))


def get_lin_similarity(word_a, word_b):
    """
    :return Lin similarity, in range[0,1]
    :param word_a [string]
    :param word_b [string]
    """

    if not checker(word_a, word_b):
        return 0

    scores = set()
    scores.add(0)
    for synset_a in get_synsets_list_from_string(word_a):
        for synset_b in get_synsets_list_from_string(word_b):
            try:
                scores.add(synset_a.lin_similarity(synset_b, semcor_ic))
            except:
                continue

    return max(scores)


def get_wu(word_a, word_b):
    if not checker(word_a, word_b):
        return 0

    scores = set()
    scores.add(0)

    synset_a_list = get_synsets_list_from_string(word_a)
    synset_b_list = get_synsets_list_from_string(word_b)

    if len(synset_a_list) == 0:
        synset_a_list = [get_synset_from_string(word_a)]
    if len(synset_b_list) == 0:
        synset_b_list = [get_synset_from_string(word_b)]

    if synset_a_list is None or synset_b_list is None:
        return 0

    for synset_a in synset_a_list:
        for synset_b in synset_b_list:
            try:
                scores.add(synset_a.wup_similarity(synset_b))
                scores.add(synset_b.wup_similarity(synset_a))
            except:
                continue

    return max(scores)


def get_wu_palmer_similarity(word_a, word_b):
    """
    :return wu & palmer similarity, in range [0,1]
    :param word_a [string]
    :param word_b [string]
    """
    if not checker(word_a, word_b):
        return 0

    synset_a = get_synset_from_string(word_a)
    synset_b = get_synset_from_string(word_b)

    if synset_a is None or synset_b is None:
        return 0

    score = synset_a.wup_similarity(synset_b)

    if score is None:
        score = synset_b.wup_similarity(synset_a)
        if score is None:
            return 0
        else:
            return score
    else:
        return score


def get_synsets_list_from_string(word):
    to_return = []
    for synset in wordnet.synsets(word):
        if synset.name().__contains__(word):
            to_return.append(synset)

    return to_return


def get_synset_from_string(word):
    """
    it is used to transform word[string format] to synset form[Synset('')], used by many nltk  function
     i.e. wordnet.lin_similarity, wordnet.wup_similarity
     It return first Synset that contains str in name

    :param word: string
    :return: in example cat -> Synset('cat.n.01')
    """
    for synset in wordnet.synsets(word):
        if synset.name().__contains__(word):
            return synset

    if wordnet.synsets(word).__len__() == 0:
        return None
    else:
        return wordnet.synsets(word)[0]


def get_subprocess(node, diagram):
    sub_process_nodes = get_nodes(diagram, ['subProcess'])
    for sub_proc in sub_process_nodes:
        if sub_proc['node_ids'].__contains__(node['id']):
            return sub_proc

    return None


def get_nodes(diagram, active_components=["all"], has_label=True):
    """

    :param diagram: BPMN diagram loaded wiith bpmn_python
    :param active_components: list of node types to retive
    :param has_label: not implemented now
    :return: nodes retrived from diagram
    """
    nodes_to_return = []
    try:
        for nodeId in diagram.diagram_graph.node:
            if diagram.diagram_graph.node[nodeId]['type'] in active_components:
                if has_label:
                    if diagram.diagram_graph.node[nodeId]['node_name'].__len__() > 0:
                        nodes_to_return.append(diagram.diagram_graph.node[nodeId])
                else:
                    nodes_to_return.append(diagram.diagram_graph.node[nodeId])  # node[nodeName].id==nodeName
            elif active_components.__contains__("all") and not diagram.diagram_graph.node[nodeId][
                                                                   'type'] == "participant":
                if has_label:
                    if diagram.diagram_graph.node[nodeId]['node_name'].__len__() > 0:
                        nodes_to_return.append(diagram.diagram_graph.node[nodeId])
                else:
                    nodes_to_return.append(diagram.diagram_graph.node[nodeId])

        return nodes_to_return
    except:
        return []


def get_hashable_nodes(diagram, active_components, has_label=True):
    nodes = get_nodes(diagram, active_components, has_label)

    id_node = dict()
    for n in nodes:
        id_node[n['id']] = n

    return id_node


def checker(word_a, word_b):
    '''
    chcek words length
    check if arguments are null

    :param word_a:
    :param word_b:
    :return: False if something is wrong, True if evertything is ok
    '''
    if word_a is None:
        return False
    elif word_b is None:
        return False
    elif len(word_a) == 0:
        return False
    elif len(word_b) == 0:
        return False
    else:
        return True


def get_verbs(tokens):
    """
    Get verbs list from list of tokens with nltk.pos_tag()
    :param tokens:
    :return:
    """
    verbs = []
    for word, position in nltk.pos_tag(tokens):
        if position in ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]:
            verbs.append(word)
    return verbs


def get_nouns(tokens):
    """
    Get nouns list from list of tokens with nltk.pos_tag()
    :param tokens:
    :return:
    """
    nouns = []
    for word, position in nltk.pos_tag(tokens):
        if position in ["NN", "NNS", "NNP", "NNPS"]:
            nouns.append(word)
    return nouns


def get_adjectives(tokens):
    """
    Get adjectives list from list of tokens with nltk.pos_tag()
    :param tokens:
    :return:
    """
    adjectives = []
    for word, position in nltk.pos_tag(tokens):
        if position in ["JJ", "JJR", "JJS"]:
            adjectives.append(word)
    return adjectives


def is_synonym(w1, w2):
    """
    :param w1:
    :param w2:
    :return: boolean value, that tells if w1 is synonym of w2 or vice versa
    """
    for synset in wordnet.synsets(w1):
        if synset.lemma_names().__contains__(w2):
            return True
    for synset in wordnet.synsets(w2):
        if synset.lemma_names().__contains__(w1):
            return True
    return False


def is_hyponym(entry, word_to_check):
    """
 print(hit.path_similarity(slap, simulate_root=False))
  Return a score denoting how similar two word senses are, based on the shortest path that connects the senses in the is-a (hypernym/hypnoym) taxonomy
    :param entry:
    :param word_to_check:
    :return: boolean value
    """

    for etymology in entry:
        for definition in etymology['definitions']:
            for relatedWords in definition['relatedWords']:
                if relatedWords['relationshipType'] == 'hyponyms':
                    if relatedWords['words'].__contains__(word_to_check):
                        return True

    return False


def get_wiktionary_entry(word):
    return wiktionary_parser.fetch(word)


def is_etymologically_related(entry, wordToCheck):
    """
    Check if word w2 appear in w1 etymolody related words, based on wiktionary entry

    :param w1:
    :param w2:
    :return:
    """

    """
    dla lower case działą lepiej
    wg. refmod mine autora, użyh lemma
    """

    for etymology in entry:
        for definition in etymology['definitions']:
            for relatedWords in definition['relatedWords']:
                if relatedWords['relationshipType'] == 'related terms':
                    for w in relatedWords['words']:
                        if w.__contains__(wordToCheck):
                            return True


    return False


def edit_distance_norm(word_a, word_b):
    """

    :param word_a:
    :param word_b:
    :return:     Returns how two words are dissimilar, based on Levenstein distance. It normalise Levenstein distance to [0,1] range
    To get how word1 and word_b are similar, do 1-returned_score
    """

    distance = edit_distance(word_a, word_b)

    max_str_length = max(word_a.__len__(), word_b.__len__())

    # normalized to range [0,1]
    score = distance / max_str_length
    #
    # in e.g. edit_distance(cat,cat)==0 and  to return 1.0 for the same words simply 1-edit_distance_norm(cat,cat)
    return score


def get_current_to_start_node(node, graph, diagram, check_for_subprocess=False):
    """
        WARNING IF YOU DIAGRAM HAS SUBPROCESSES YOU NEDD TO FLAG IT
    :param check_for_subprocess: flag
    :param graph: diagram in graph format
    :param node: node in diagram
    :param diagram: diagram,
    :return: length from node to (first) start node
    """
    start_node = get_nodes(diagram, ["startEvent"])
    if check_for_subprocess:
        used_node = get_subprocess(node, diagram)
        if used_node is None:
            used_node = node
    else:
        used_node = node

    if not start_node:
        return 0
    else:
        try:
            d = nx.shortest_path_length(graph, used_node['id'], start_node[0]['id'], weight=None)
            if d == 0 or d is None:
                return 0
            else:
                return d
        except:
            return 0


def get_current_to_end_node(node, graph, diagram, check_for_subprocess=False):
    """
        WARNING IF YOU DIAGRAM HAS SUBPROCESSES YOU NEDD TO FLAG IT
    :param check_for_subprocess: flag
    :param graph:
    :param node: node in diagram
    :param diagram:
    :return: length from node to (first) end node
    """
    if check_for_subprocess:
        used_node = get_subprocess(node, diagram)
        if used_node is None:
            used_node = node
    else:
        used_node = node

    end_node = get_nodes(diagram, ["endEvent"])
    if not end_node:
        return 0
    else:
        try:
            d = nx.shortest_path_length(graph, used_node['id'], end_node[0]['id'], weight=None)
            if d == 0 or d is None:
                return 0
            else:
                return d
        except:
            return 0


def get_graph_with_id_nodes(diagram):
    """
    Change diagram into graph format, so it is easier to calculate things like distances with networkx functions.
    WARNING IF YOU DIAGRAM HAS SUBPROCESSES YOU NEDD TO FLAG IT
    :param diagram:
    :return:
    """
    graph = nx.Graph()
    for node in diagram.diagram_graph.node:
        graph.add_node(node)

    for from_edge in diagram.diagram_graph.edge:

        for to_edge in diagram.diagram_graph.edge[from_edge]:
            graph.add_edge(from_edge, to_edge)

    return graph
