# -*- coding: utf-8 -*-
from __future__ import division
import commonFunctions
import matcher
from nltk.corpus import brown
from wiktionaryparser import WiktionaryParser

# consideredComponents = ['all']#consider task,event,subProcess
consideredComponents = ['task']
verbs = []
nouns = []
adjectives = []

for word, pos in brown.tagged_words():
    if pos.startswith('VB'):
        verbs.append(word)
    elif pos.startswith('JJ'):
        adjectives.append(word)
    elif pos.startswith('N') and not pos.startswith('NC'):
        nouns.append(word)

wiki_entries = dict()  # (lemma, JSON)
wiktionary_parser = WiktionaryParser()


class node():
    id = ""
    type = ""
    verbsList = []
    nounsList = []
    adjectivesList = []
    labelTokens = []

    def __init__(self, id, type, verbs, nouns, adjectives, tokens):
        self.id = id
        self.type = type
        self.adjectivesList = adjectives
        self.labelTokens = tokens
        self.nounsList = nouns
        self.verbsList = verbs

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'type') == self.type and
                getattr(other, 'verbsList') == self.verbsList and
                getattr(other, 'nounsList') == self.nounsList and
                getattr(other, 'adjectivesList') == self.adjectivesList and
                getattr(other, 'labelTokens') == self.labelTokens)

    def __hash__(self):
        return hash(self.node1.__hash__ + self.node2.__hash__)


def get_refmod_mine_nlm_matches(model1, model2):
    matches = []

    nodes1temp = commonFunctions.get_nodes(model1, consideredComponents)
    nodes2temp = commonFunctions.get_nodes(model2, consideredComponents)
    nodes1 = create_refmod_nodes(nodes1temp)
    nodes2 = create_refmod_nodes(nodes2temp)

    entries1 = [node_a.labelTokens for node_a in nodes1]
    entries2 = [node_b.labelTokens for node_b in nodes2]

    global wiki_entries
    wiki_entries = fetch_entry_from_wiktionary(entries1 + entries2)

    for n1 in nodes1:
        for n2 in nodes2:
            if is_identical_condition(n1, n2):
                matches.append(
                    matcher.match(node1=model1.diagram_graph.node[n1.id], node2=model2.diagram_graph.node[n2.id],
                                  score=1.0))
                continue
            if is_cross_category_condition(n1, n2):
                matches.append(
                    matcher.match(node1=model1.diagram_graph.node[n1.id], node2=model2.diagram_graph.node[n2.id],
                                  score=1.0))
                continue

    return matches


def create_refmod_nodes(nodes):
    nodes_list = []
    for n in nodes:
        # step #1 tokenizastion and lemmization
        try:
            tokens = commonFunctions.lemminisation(commonFunctions.get_tokens(n['node_name']))
        except:
            print(n)
        # retiving syntacit info
        n_node = node(
            id=n['id'],
            type=n['type'],
            verbs=get_verbs(tokens),
            nouns=get_nouns(tokens),
            adjectives=get_adjectives(tokens),
            tokens=tokens
        )
        nodes_list.append(n_node)
    return nodes_list


def words_correspond(word1, word2):
    """"
    to check if two words coreespond their lexical relation is checked. only one condition is needed to pass
    """

    if word1.__eq__(word2):
        return True
    if commonFunctions.is_synonym(word1, word2) | commonFunctions.is_synonym(word2, word1):
        return True
    if is_hyponym(word1, word2) | is_hyponym(word2, word1):
        return True
    if is_etymologically_related(word1, word2) | is_etymologically_related(word2, word1):
        return True
    return False


def words_lists_corresponds(list_a, list_b):
    ''''
    check if each word from list_a corespond to at least one word in list_b
    '''
    for word_a in list_a:
        word_a_counter = 0
        for word_b in list_b:
            if words_correspond(word_a, word_b):
                word_a_counter += 1
        if word_a_counter < 1:
            return False

    return True


def is_identical_condition(n1, n2):
    # every noun of NN1 corresponds to at least one noun of NN2 and the other way around
    condition1 = words_lists_corresponds(n1.nounsList, n2.nounsList) and words_lists_corresponds(n2.nounsList,
                                                                                                 n1.nounsList)
    # 'every verb of V B1 corresponds to at least one verb of V B2 and the other way around'
    condition2 = words_lists_corresponds(n1.verbsList, n2.verbsList) and words_lists_corresponds(n2.verbsList,
                                                                                                 n1.verbsList)
    # 'every adjective of JJ1 corresponds to at least one adjective of JJ2 and the other way around'
    condition3 = words_lists_corresponds(n1.adjectivesList, n2.adjectivesList) and words_lists_corresponds(
        n2.adjectivesList, n1.adjectivesList)

    return condition1 and condition2 and condition3


def is_cross_category_condition(n1, n2):
    '''
    l_1 == n1.labelTokens
    l_2 == n2.labelTokens
    :param n1:
    :param n2:
    :return:
    '''
    condition1 = False
    condition2 = False
    if n1.adjectivesList.__len__() == 1 or n1.verbsList.__len__() == 1:
        if n2.labelTokens.__len__() <= 2:
            word_correspondace_count = []
            for noun in n2.nounsList:
                inside_counter = 0
                for word in n1.labelTokens:
                    if words_correspond(noun, word):
                        inside_counter += 1
                word_correspondace_count.append(inside_counter)

            if word_correspondace_count.__contains__(1):
                condition1 = True

    if n2.adjectivesList.__len__() == 1 or n2.verbsList.__len__() == 1:
        if n1.labelTokens.__len__() <= 2:
            word_correspondace_count = []
            for noun in n1.nounsList:
                inside_counter = 0
                for word in n2.labelTokens:
                    if words_correspond(noun, word):
                        inside_counter += 1
                word_correspondace_count.append(inside_counter)

            if word_correspondace_count.__contains__(1):
                condition2 = True

    # By default return False
    return condition1 or condition2


def fetch_entry_from_wiktionary(list_of_lists):
    lemmas_set = set()
    return_dict = dict()
    for words_list in list_of_lists:
        for lemma in words_list:
            lemmas_set.add(lemma)

    for lemma in lemmas_set:
        return_dict[lemma] = wiktionary_parser.fetch(lemma)

    return return_dict


def is_hyponym(lemma, lemma_to_check):
    for etymology in wiki_entries[lemma]:
        for definition in etymology['definitions']:
            for relatedWords in definition['relatedWords']:
                if relatedWords['relationshipType'] == 'hyponyms':
                    for w in relatedWords['words']:
                        if w.__contains__(lemma_to_check):
                            return True
    return False


def is_etymologically_related(lemma, lemma_to_check):
    for etymology in wiki_entries[lemma]:
        for definition in etymology['definitions']:
            for relatedWords in definition['relatedWords']:
                if relatedWords['relationshipType'] == 'related terms':
                    for w in relatedWords['words']:
                        if w.__contains__(lemma_to_check):
                            return True
    return False


def get_verbs(tokens):
    return list(set([token for token in tokens if verbs.__contains__(token)] + commonFunctions.get_verbs(tokens)))


def get_nouns(tokens):
    return list(set([token for token in tokens if nouns.__contains__(token)] + commonFunctions.get_nouns(tokens)))


def get_adjectives(tokens):
    return list(
        set([token for token in tokens if adjectives.__contains__(token)] + commonFunctions.get_adjectives(tokens)))
