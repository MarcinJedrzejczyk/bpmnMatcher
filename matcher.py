# -*- coding: utf-8 -*-

from __future__ import division

import xml.etree.ElementTree as ET
import numpy
import os

resourceTag = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}resource'
mapTag = '{http://knowledgeweb.semanticweb.org/heterogeneity/alignment#}map'


class match():
    def __init__(self, node1, node2, score):
        self.node1 = node1
        self.node2 = node2
        self.score = score

    def __str__(self):
        return str(self.__class__) + "\n" + str(self.node1) + "\n" + str(self.node2) + "\n" + str(self.score) + "\n"

    def __hash__(self):
        return hash(self.node1['node_name']) + hash(self.node1['id']) + hash(self.node2['node_name']) + hash(
            self.node2['id']) + hash(self.score)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if getattr(other, 'node1') == self.node1 and getattr(other, 'node2') == self.node2 and getattr(other,
                                                                                                           'score') == self.score:
                return True
            elif getattr(other, 'node2') == self.node1 and getattr(other, 'node1') == self.node2 and getattr(other,
                                                                                                             'score') == self.score:
                return True
            else:
                return False
        else:
            return False


class gold_match():
    def __init__(self, entity_1_id, entity_1_model, entity_2_id, entity_2_model, score, relation="="):
        self.entity_1_id = str(entity_1_id)
        self.entity_1_model = str(entity_1_model)
        self.entity_2_id = str(entity_2_id)
        self.entity_2_model = str(entity_2_model)
        self.relation = str(relation)
        self.relation_score = float(score)

    def __hash__(self):
        return hash(self.entity_1_id) + hash(self.entity_1_model) + hash(self.entity_2_id) + hash(
            self.entity_2_model) + hash(self.relation) + hash(
            self.relation_score)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if (self.entity_1_model == getattr(other, 'entity_1_model', None) and
                    self.entity_2_model == getattr(other, 'entity_2_model', None)):

                if (self.entity_1_id == getattr(other, 'entity_1_id', None) and
                        self.entity_2_id == getattr(other, 'entity_2_id', None)):
                    # %#self.relation_score == getattr(other, 'relation_score', None)):
                    return True
                else:
                    return False


            elif (self.entity_2_model == getattr(other, 'entity_1_model', None) and
                  self.entity_1_model == getattr(other, 'entity_2_model', None)):
                if (self.entity_2_id == getattr(other, 'entity_1_id', None) and
                        self.entity_1_id == getattr(other, 'entity_2_id', None)):  # and
                    # self.relation_score == getattr(other, 'relation_score', None)):
                    return True
                else:
                    return False

            else:
                return False
        else:
            return False

        return False


def match_into_gold_match(match, process_name_1, process_name_2, bpmn1, bpmn2, score_to_one=False):
    # To make sure there is not situation like, node1=node1_id, model1=model_2_name
    if match.node1['id'] in bpmn1.diagram_graph.node:
        model1 = process_name_1
        model2 = process_name_2
    else:
        model1 = process_name_2
        model2 = process_name_1
    if not score_to_one:
        return gold_match(entity_1_id=match.node1['id'], entity_1_model=model1, entity_2_id=match.node2['id'],
                          entity_2_model=model2, score=match.score)
    else:
        return gold_match(entity_1_id=match.node1['id'], entity_1_model=model1, entity_2_id=match.node2['id'],
                          entity_2_model=model2, score=1.0)


def check_file(file_path):
    return os.path.isfile(file_path)


def load_gold_standard(file_path):

    if not check_file(file_path):
        return []
    gold = []
    tree = ET.parse(file_path)

    for elem in tree.iter(mapTag):

        for ch in elem:
            # 0 entity1, 1 entity2, 2 relation,3 measure
            e1 = ch[0].attrib[resourceTag].replace('http://', '').split('#')
            e2 = ch[1].attrib[resourceTag].replace('http://', '').split('#')
            gold.append(gold_match(entity_1_id=e1[1], entity_1_model=e1[0], entity_2_id=e2[1], entity_2_model=e2[0],
                                   relation=ch[2].text, score=ch[3].text))

    return gold


def check_gold_standard(gold_standard, matching, do_print=False):
    true_positive = 0
    # true_negative = 1
    false_positive = 0
    false_negative = 0

    f_measure = 0
    precision = 0
    recall = 0
    #
    # true negative hard to say
    # false positive m not in gold, m in matching
    # false negative m in gold, not in matching


    for m in matching:
        if gold_standard.__contains__(m):
            true_positive += 1
        else:
            false_positive += 1

    for g in gold_standard:
        if not matching.__contains__(g):
            false_negative += 1

    if true_positive + false_positive != 0:
        precision = true_positive / (true_positive + false_positive)
    if true_positive + false_negative != 0:
        recall = true_positive / (true_positive + false_negative)
    if precision + recall != 0:
        f_measure = 2 * precision * recall / (precision + recall)

    """
     It might happen that a matcher generates an empty set of correspondences. If this is the case,
    we set the precision score for computing the macro average to 1.0, due to the consideration
    that an empty set of correspondences contains no incorrect correspondences.
    """
    if len(matching) == 0:
        precision = 1

    """
     Moreover, some of the testcases of the AM data set have empty gold standards. In this case we set the
    recall score for computing the macro average to 1.0, because all correct matches have been  detected.
    """
    if gold_standard.__len__ == 0:
        recall = 1

    if do_print:
        print({'precision': precision, 'recall': recall, 'f_measure': f_measure})

    return {'precision': precision, 'recall': recall, 'f_measure': f_measure, 'TP': true_positive, 'FN': false_negative,
            'FP': false_positive}


def get_summarised_scores(scores):
    """

    :param scores: list of dicts, [{'precision': precision, 'recall': recall, 'f_measure': f_measure}]
    :return: dict { precision: {average_macro,averageOmicro,standard_deviation},
    recall: {average_macro,averageOmicro,standard_deviation},
     f_measure: {average_macro,averageOmicro,standard_deviation} }
    """
    to_return = {}
    precision = []
    recall = []
    f_measure = []
    fn_list = []
    tp_list = []
    fp_list = []

    for item in scores:
        precision.append(item['precision'])
        recall.append(item['recall'])
        f_measure.append(item['f_measure'])
        fn_list.append(item['FN'])
        tp_list.append(item['TP'])
        fp_list.append(item['FP'])

    fn = sum(fn_list)
    fp = sum(fp_list)
    tp = sum(tp_list)
    precision_micro = tp / (tp + fp)
    recall_micro = tp / (tp + fn)
    if (precision_micro + recall_micro) != 0:
        f1_micro = 2 * precision_micro * recall_micro / (precision_micro + recall_micro)
    else:
        f1_micro = 0
    to_return['precision'] = {'avg-macro': numpy.mean(precision), 'avg-micro': precision_micro,
                              'sd': numpy.std(precision, axis=0)}
    to_return['recall'] = {'avg-macro': numpy.mean(recall), 'avg-micro': recall_micro, 'sd': numpy.std(recall, axis=0)}
    to_return['f_measure'] = {'avg-macro': numpy.mean(f_measure), 'avg-micro': f1_micro,
                              'sd': numpy.std(f_measure, axis=0)}

    return to_return
