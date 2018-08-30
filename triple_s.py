# -*- coding: utf-8 -*-
from __future__ import division

import commonFunctions
import numpy
import matcher

activeComponents = ['task', 'subProcess']


def get_triple_s_matches(bpmn1, bpmn2, syntactic_weight=0.5, semantic_weight=0.35, ratio_weight=0.05,
                         position_weight=0.1,
                         threshold=0.5):
    matches = []
    nodes1 = commonFunctions.get_nodes(bpmn1, activeComponents)
    nodes2 = commonFunctions.get_nodes(bpmn2, activeComponents)
    graph1 = commonFunctions.get_graph_with_id_nodes(bpmn1)
    graph2 = commonFunctions.get_graph_with_id_nodes(bpmn2)

    for node_a in nodes1:
        for node_b in nodes2:
            l1 = node_a['node_name'].lower()
            l2 = node_b['node_name'].lower()
            syntactic_score = get_syntactic_score(l1, l2)
            semantic_score = get_semantic_score(l1, l2)

            structural_score = get_structural_score(node_a, node_b, graph_a=graph1, graph_b=graph2, bpmn_a=bpmn1,
                                                    bpmn_b=bpmn2,
                                                    ratio_weight=ratio_weight,
                                                    position_weight=position_weight)

            final_score = syntactic_weight * syntactic_score + semantic_weight * semantic_score + structural_score

            if final_score >= threshold:
                matches.append(matcher.match(node1=node_a, node2=node_b, score=final_score))

    return matches


def get_syntactic_score(label_a, label_b):
    # Preprocessing step
    tokens_a = commonFunctions.get_tokens_without_stop_words(label_a)
    tokens_b = commonFunctions.get_tokens_without_stop_words(label_b)
    scores = []
    for word_a in tokens_a:
        row = []
        for word_b in tokens_b:
            sc = commonFunctions.edit_distance_norm(word_a, word_b)  # the returned score is how two string differ
            row.append(sc)
        scores.append(row)

    # calculate final score
    max_word_count = max(len(tokens_a), len(tokens_b))
    min_score = calculate_min_xim(scores)
    score = min_score / max_word_count
    # The final syntactic score is the minimum distance over all tokens divided by
    # the number of tokens, i.e. the minimum average distance between each token

    return 1 - score


def get_semantic_score(label_a, label_b):
    tokens_a = commonFunctions.get_tokens_without_stop_words(label_a)
    tokens_b = commonFunctions.get_tokens_without_stop_words(label_b)
    scores = []
    for word_a in tokens_a:
        row = []
        for word_b in tokens_b:
            sc = commonFunctions.get_wu_palmer_similarity(word_a, word_b)
            row.append(sc)
        scores.append(row)

    max_words_count = max(len(tokens_a), len(tokens_b))
    similarity = calculate_max_xim(scores)
    score = similarity / max_words_count

    # The final semantic score is the maximum average similarity analogous to the final syntactic score
    return score


def get_structural_score(label_a, label_b, graph_a, graph_b, bpmn_a, bpmn_b, ratio_weight, position_weight):
    # calculate arc relation similarity
    in_a = label_a['incoming'].__len__()
    in_b = label_b['incoming'].__len__()
    out_a = label_a['outgoing'].__len__()
    out_b = label_b['outgoing'].__len__()

    if max(out_a, out_b) != 0:
        outgoing_ratio = 1.0 - abs(out_a - out_b) / max(out_a, out_b)
    else:
        outgoing_ratio = 1.0
    if max(in_a, in_b) != 0:
        incoming_ratio = 1.0 - abs(in_a - in_b) / max(in_a, in_b)
    else:
        incoming_ratio = 1.0
    score_ratio = (outgoing_ratio + incoming_ratio) / 2

    relative_1 = get_relative_pos(label_a, graph_a, bpmn_a)
    relative_2 = get_relative_pos(label_b, graph_b, bpmn_b)

    if relative_1 == 0 or relative_2 == 0:
        position_score = 0
    elif relative_1 >= relative_2:
        position_score = relative_2 / relative_1
    else:
        position_score = relative_1 / relative_2

    score = ratio_weight * score_ratio + position_weight * position_score
    return score


def get_relative_pos(node, graph, diagram):
    # Warning IT WILL USE FIRST STAR NODE AND FIRST END NODE IT WILL FIND
    sub_process = commonFunctions.get_subprocess(node, diagram)
    if sub_process is None:
        to_start = commonFunctions.get_current_to_start_node(node, graph, diagram)
        to_end = commonFunctions.get_current_to_end_node(node, graph, diagram)
    else:
        to_start = commonFunctions.get_current_to_start_node(sub_process, graph, diagram)
        to_end = commonFunctions.get_current_to_end_node(sub_process, graph, diagram)
    if to_start + to_end == 0:
        return 1
    relative_position = to_start / (to_start + to_end)
    return relative_position


def calculate_max_xim(scores):
    max_total = 0
    x = numpy.array(scores)

    calculate = True
    while calculate:

        y_len, x_len = x.shape
        i, j = numpy.unravel_index(x.argmax(), x.shape)
        max_current = x[i, j]

        if y_len == 1:
            max_total += max_current
            calculate = False
        elif x_len == 1:
            max_total += max_current
            calculate = False
        else:
            max_total += max_current

            new_x = numpy.delete(x, i, 0)
            new_x = numpy.delete(new_x, j, 1)
            x = new_x

    return max_total


def calculate_min_xim(scores):
    min_total = 0
    x = numpy.array(scores)

    calculate = True
    while calculate:

        y_len, x_len = x.shape
        i, j = numpy.unravel_index(x.argmin(), x.shape)
        min_current = x[i, j]

        if y_len == 1:
            min_total += min_current + x_len - 1
            calculate = False
        elif x_len == 1:
            min_total += min_current + y_len - 1
            calculate = False
        else:
            min_total += min_current
            new_x = numpy.delete(x, i, 0)
            new_x = numpy.delete(new_x, j, 1)
            x = new_x

    return min_total
