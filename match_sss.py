# -*- coding: utf-8 -*-
from __future__ import division
import commonFunctions
import matcher
from triple_s import calculate_min_xim, calculate_max_xim

activeComponents = ['all']

word_net_priority = .7


def getMatchSSSmatches(diagram1, diagram2, threshold=0.5):
    # bag has structure: {nodeId: normalizedLabel}
    bag1 = extract_normalize_step(diagram1, activeComponents)

    bag2 = extract_normalize_step(diagram2, activeComponents)

    matches_alpha = calculate_similarity_step(bag1, bag2)

    # Identify step
    matches_final = []

    for m in matches_alpha:
        if m.similiraty_score >= threshold:
            matches_final.append(
                matcher.match(node1=diagram1.diagram_graph.node[m.id1], node2=diagram2.diagram_graph.node[m.id2],
                              score=m.similiraty_score))

    return matches_final


def extract_normalize_step(diagram, active):
    nodes = commonFunctions.get_nodes(diagram, active)
    bag = dict()
    for node in nodes:
        label = node['node_name'].lower()
        wr = commonFunctions.get_tokens_without_stop_words(label)
        bag[node['id']] = commonFunctions.lemminisation(commonFunctions.stemming(wr))

    return bag


def calculate_similarity_step(bag1, bag2):
    matches = []

    for key1 in bag1.keys():
        for key2 in bag2.keys():

            # loops for two labels
            lin_scores = []
            lev_scores = []
            for wordA in bag1[key1]:
                lin_row = []
                lev_row = []
                for wordB in bag2[key2]:
                    # score_word = calculate_similarity(wordA, wordB)
                    lin_row.append(commonFunctions.get_lin_similarity(wordA, wordB))
                    lev_row.append(commonFunctions.edit_distance_norm(wordA, wordB))
                    # matches_scores.append(score_word)
                lin_scores.append(lin_row)
                lev_scores.append(lev_row)

            max_words_count = max(len(bag1[key1]), len(bag2[key2]))

            lin_temp = calculate_max_xim(lin_scores)
            lin_score = lin_temp / max_words_count

            lev_temp = calculate_min_xim(lev_scores)
            lev_score = 1 - lev_temp / max_words_count

            score_label = aggregate(score_lin=lin_score, score_lev=lev_score,
                                    wordnet_priority=word_net_priority)

            matches.append(match(label1=bag1[key1], label2=bag2[key2], id1=key1, id2=key2, sim=score_label))

    return matches


def aggregate(score_lev, score_lin, wordnet_priority):
    """"
        Here is aggreagation step. Algorithm author made word net based similarity priority
    """
    if score_lin > wordnet_priority:
        return score_lin
    elif score_lin > score_lev:
        return score_lin
    else:
        return score_lev


class match():
    def __init__(self, label1, id1, label2, id2, sim):
        self.id1 = id1
        self.id2 = id2
        self.label1 = label1
        self.label2 = label2
        self.similiraty_score = sim
