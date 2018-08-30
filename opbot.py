# -*- coding: utf-8 -*-
from __future__ import division
from numpy import median, mean
import commonFunctions as cf
import matcher
import cco_similarity as cco

active_components = ['task','subProcess']#all vs task,event
#active_components = ['all']


class models_pair:
    def __init__(self, model1, bpmn1, model2, bpmn2):
        self.model1 = model1
        self.bpmn1 = bpmn1
        self.model2 = model2
        self.bpmn2 = bpmn2
        self.activities_pairs = []


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.model1 == getattr(other, 'model1', None) and self.model2 == getattr(other, 'model2', None):
                return True
            elif self.model1 == getattr(other, 'model2', None) and self.model2 == getattr(other, 'model1', None):
                return True
            else:
                return False
        else:
            return False

    def __hash__(self):
        return hash(self.model1) + hash(self.model2)


class activity_pair:
    def __init__(self, pair, node1, label1, st1, tokens1, node2, label2, st2, tokens2):
        self.model_pair = pair
        self.node1_id = node1
        self.label1 = label1  # label has node label in that was tokenised,stemmed, and had stop word deleted
        self.tokens1 = tokens1
        self.start_distance1 = st1
        self.node2_id = node2
        self.label2 = label2
        self.tokens2 = tokens2
        self.start_distance2 = st2


def prune(scores, length):
    scores_sorted = sorted(scores)
    return scores_sorted[(scores.__len__() - length):scores.__len__()]


def calculate_similarity(matcher, activity_pair, do_word_pruning, ccc_matcher_object=None):
    scores1 = [0 for i in range(activity_pair.label1.__len__())]
    scores2 = [0 for i in range(activity_pair.label2.__len__())]

    label1 = activity_pair.label1
    label2 = activity_pair.label2
    if matcher == 'CCO':
        label1 = activity_pair.tokens1
        label2 = activity_pair.tokens2

    i = 0
    for wordA in label1:

        j = 0
        for wordB in label2:
            if matcher == 'LEV':
                sim = 1 - cf.edit_distance_norm(wordA, wordB)
            elif matcher == 'LIN':
                sim = cf.get_lin_similarity(wordA, wordB)
            elif matcher == 'CCO':
                sim = ccc_matcher_object.get_cco_similarity(wordA, wordB)
            else:
                sim = 0
            scores1[i] = max(scores1[i], sim)
            scores2[j] = max(scores2[j], sim)
            j += 1
        i += 1

    if do_word_pruning:
        if scores1.__len__() > scores2.__len__():
            scores1 = prune(scores1, scores2.__len__())
        elif scores2.__len__() > scores1.__len__():
            scores2 = prune(scores2, scores1.__len__())

    sum_score = sum(scores1 + scores2)

    return sum_score / (scores1.__len__() + scores2.__len__())


def get_BOT_results(activity_pairs_all, models, used_matcher, do_word_prunning=False, cco_matcher=None):
    results = {}  # {activity_pair:score}

    for activity_pair_for in activity_pairs_all:
        sim = calculate_similarity(used_matcher, activity_pair_for, do_word_prunning, cco_matcher)
        results[activity_pair_for] = sim

    # {activityPair: sim_score} -- {object:double_value}
    return results


def determine_pairs_threshold(activity_pairs):
    threshs = set()
    for pair_key in activity_pairs.keys():
        threshs.add(activity_pairs[pair_key])

    return sorted(threshs)


def determine_thresholds(bot_results, models, pre_t_min, pre_t_max):
    '''

    :param bot_results: {activity_pair:sim:score}
    :param models: [model_pair]
    :param pre_t_min: double
    :param pre_t_max: double
    :return: (final_threshold,order_relation_score) tuple
    '''
    threshes = determine_pairs_threshold(bot_results)

    min_t = max(filter(lambda a: a < pre_t_min, threshes))
    max_t = max(filter(lambda a: a < pre_t_max, threshes))

    threshold_to_check = [x for x in threshes if x > min_t and x < max_t]

    threhshold_score = {}

    for temp_thresh in threshold_to_check:
        threhshold_score[temp_thresh] = get_order_relation_score(bot_results, models, temp_thresh)

    final_threshold = max(threhshold_score.iterkeys(), key=(lambda key: threhshold_score[key]))

    # consider situtaion whre more than 1 threshold got MAX score
    temp_dict = {}
    for temp_thresh in threhshold_score.keys():
        if threhshold_score[temp_thresh] == threhshold_score[final_threshold]:
            temp_dict[temp_thresh] = threhshold_score[temp_thresh]

    if len(temp_dict)>1:
        sorted_keys=sorted(temp_dict.keys(),reverse=True)
        return (sorted_keys[0], threhshold_score[final_threshold])
    else:
        return (final_threshold, threhshold_score[final_threshold])


def get_model_pair_ORS(bot_results, mod_pair, threshold):
    num_of_calculations = 0
    score = 0
    to_consider = []

    for task_pair in mod_pair.activities_pairs:

        if bot_results[task_pair] >= threshold:
            to_consider.append(task_pair)

    for i in range(0, to_consider.__len__() - 1):
        activity_pair_A = to_consider[i]
        for j in range(i + 1, to_consider.__len__()):
            activity_pair_B = to_consider[j]
            num_of_calculations += 1

            result = (activity_pair_A.start_distance1 - activity_pair_B.start_distance1) * (
                    activity_pair_A.start_distance2 - activity_pair_B.start_distance2)
            if result >= 0:
                score += 1
            else:
                score += 0

    if num_of_calculations == 0:
        return 0
    else:
        return score / num_of_calculations


def get_order_relation_score(bot_results, models, threshold):
    ORS = 0.0
    for mod_pair in models:
        ORS += get_model_pair_ORS(bot_results, mod_pair, threshold)

    return ORS / models.__len__()


def get_two_best_thresholds(bot_threshold,bot_results):
    '''
    Rank BOT configurations in descending order, based on theis order relation score
    :param bot_results:
    :param bot_threshold: {configuration: (threshold, ORS_Score)}
    :return: (best_conf,second_best_conf)
    '''
    sor = sorted(bot_threshold.items(), key=lambda x: x[1][1], reverse=True)
    max_ors=sor[0][1][1]
    to_reconsider=[]
    for configuration in bot_threshold.keys():
        if bot_threshold[configuration][0]==max_ors:
            to_reconsider.append(configuration)
    #more than two configurations with max score
    if len(to_reconsider)>2:
        config_matches_count=dict()
        for bot_config in to_reconsider:
            matches_count=len([x for x in bot_results[bot_config].values() if x >= bot_threshold[configuration]])
            if matches_count>0:
                config_matches_count[config_matches_count]=matches_count
        #get two configuration with the smallest number of matches
        sor_2=sorted(config_matches_count, key=lambda key: config_matches_count[key])

        if len(sor_2)>=2:
            return sor_2[0],sor_2[1]
        else:
            return (sor[0][0], sor[1][0])

    return (sor[0][0], sor[1][0])


def get_matches_by_combine(activity_pairs_all, bots_results, bot_thresholds, best, second_best, model_pairs):
    final_matches = dict()
    for pair in model_pairs:
        final_matches[pair] = []

    for act_pair in activity_pairs_all:
        # bots_results[best][act_pair] , return similarity score of act_pair in best BOT configufarion
        if bots_results[best][act_pair] >= bot_thresholds[best][0] or bots_results[second_best][act_pair] >= \
                bot_thresholds[second_best][0]:
            sim_score = max(bots_results[best][act_pair], bots_results[second_best][act_pair])
            node1 = act_pair.model_pair.bpmn1.diagram_graph.node[act_pair.node1_id]
            node2 = act_pair.model_pair.bpmn2.diagram_graph.node[act_pair.node2_id]
            final_matches[act_pair.model_pair].append(matcher.match(node1=node1, node2=node2, score=sim_score))

    return final_matches


def get_models_from_pairs(pairs):
    to_return = {}
    for pair in pairs:
        to_return[pair.model1] = pair.bpmn1
        to_return[pair.model2] = pair.bpmn2
    return to_return


def get_model_pairs(models):
    model_pairs = set()
    for model_name in models.keys():
        for model_name_2 in models.keys():
            if not model_name.__eq__(model_name_2):
                model_pairs.add(models_pair(model1=model_name, bpmn1=models[model_name], model2=model_name_2,
                                            bpmn2=models[model_name_2]))
    return model_pairs


def get_opbot_matches(dataset, model_pairs=None):
    # define models pairs, model1--model2
    # get model - activities
    # to  model1--model add acivity pairs, model1_task1--model2_task1 ... ect
    models = dataset  # i assume the models are loaded already
    if model_pairs is None:
        model_pairs = get_model_pairs(models)


    model_activity = {}  # model_id:{node_id:node}
    for model_name in models.keys():
        model_activity[model_name] = cf.get_hashable_nodes(models[model_name], active_components)

    final_matches = dict()
    for pair in model_pairs:
        final_matches[pair] = []


    # make copy of nodes kyes, later delete keys of nodes that have been filtered out
    nodes_keys = {}
    for pair in model_pairs:
        nodes_keys[pair] = {}
        nodes_keys[pair][pair.model1] = model_activity[pair.model1].keys()  # .copy()
        nodes_keys[pair][pair.model2] = model_activity[pair.model2].keys()  # .copy()

    # create a list of all tokenised labels from all models
    # used to create coocurance dictionary
    all_labels = []
    for model_id in models.keys():
        for node_id in model_activity[model_id].keys():
            all_labels.append(cf.get_tokens_without_stop_words(model_activity[model_id][node_id]['node_name'].lower()))

    all_words_set = set()  # used later to create coocurance dict

    for m_pair in model_pairs:
        model1 = m_pair.model1
        model2 = m_pair.model2

        for node1 in model_activity[model1].keys():
            tokens = cf.get_tokens_without_stop_words(model_activity[model1][node1]['node_name'])

            for node2 in model_activity[model2].keys():

                for a_word in tokens + cf.get_tokens_without_stop_words(model_activity[model2][node2]['node_name']):
                    all_words_set.add(a_word.lower())
                # Filtering step
                if model_activity[model1][node1]['node_name'] == model_activity[model2][node2]['node_name']:
                    # nodes with identical labels are matched
                    final_matches[m_pair].append(
                        matcher.match(model_activity[model1][node1], model_activity[model2][node2],
                                      1.0))

                    if nodes_keys[m_pair][model1].__contains__(node1):
                        nodes_keys[m_pair][model1].remove(node1)
                    if nodes_keys[m_pair][model2].__contains__(node2):
                        nodes_keys[m_pair][model2].remove(node2)

    # normalise labels for remaning nodes
    # create variable , {model: {node_id:normalised_label}}
    labels = {}
    for model_name in models:
        labels[model_name] = {}
        for node in model_activity[model_name].keys():
            labels[model_name][node] = cf.stemming(
                cf.get_tokens_without_stop_words(model_activity[model_name][node]['node_name'].lower()))

    # Extract activity pairs
    activity_pairs_all = []
    for pair in model_pairs:
        nodes1_keys = nodes_keys[pair][pair.model1]
        nodes2_keys = nodes_keys[pair][pair.model2]
        for node1 in nodes1_keys:
            for node2 in nodes2_keys:
                graph1 = cf.get_graph_with_id_nodes(pair.bpmn1)
                graph2 = cf.get_graph_with_id_nodes(pair.bpmn2)
                n1 = model_activity[pair.model1][node1]
                n2 = model_activity[pair.model2][node2]
                tokens1 = cf.get_tokens_without_stop_words(model_activity[pair.model1][node1]['node_name'].lower())
                tokens2 = cf.get_tokens_without_stop_words(model_activity[pair.model2][node2]['node_name'].lower())
                st1 = cf.get_current_to_start_node(node=n1, graph=graph1, diagram=pair.bpmn1)
                st2 = cf.get_current_to_start_node(node=n2, graph=graph2, diagram=pair.bpmn2)
                new_activity_pair = activity_pair(pair=pair, node1=node1, label1=labels[pair.model1][node1],
                                                  st1=st1, tokens1=tokens1,
                                                  node2=node2, label2=labels[pair.model2][node2], st2=st2,
                                                  tokens2=tokens2)
                activity_pairs_all.append(new_activity_pair)
                pair.activities_pairs.append(new_activity_pair)

    coocurance = cco.get_coocccurance_dict(all_words_set, all_labels)
    cco_matcher = cco.cco_occurance_similarity_calculator(coocurance, 2)

    # calculate similarities
    bots_results = {}
    bots_results['B1'] = get_BOT_results(activity_pairs_all, models, 'LIN', False)
    bots_results['B2'] = get_BOT_results(activity_pairs_all, models, 'LIN', True)
    bots_results['B3'] = get_BOT_results(activity_pairs_all, models, 'LEV', False)
    bots_results['B4'] = get_BOT_results(activity_pairs_all, models, 'LEV', True)
    bots_results['B5'] = get_BOT_results(activity_pairs_all, models, 'CCO', False, cco_matcher)
    bots_results['B6'] = get_BOT_results(activity_pairs_all, models, 'CCO', True, cco_matcher)

    # determine thresholds
    bot_thresholds = {}
    bot_thresholds['B1'] = determine_thresholds(bot_results=bots_results['B1'], models=model_pairs, pre_t_min=0.6,
                                                pre_t_max=1)
    bot_thresholds['B2'] = determine_thresholds(bot_results=bots_results['B2'], models=model_pairs, pre_t_min=0.6,
                                                pre_t_max=1)
    bot_thresholds['B3'] = determine_thresholds(bot_results=bots_results['B3'], models=model_pairs, pre_t_min=0.6,
                                                pre_t_max=1)
    bot_thresholds['B4'] = determine_thresholds(bot_results=bots_results['B4'], models=model_pairs, pre_t_min=0.6,
                                                pre_t_max=1)
    bot_thresholds['B5'] = determine_thresholds(bot_results=bots_results['B5'], models=model_pairs, pre_t_min=0.7,
                                                pre_t_max=1)
    bot_thresholds['B6'] = determine_thresholds(bot_results=bots_results['B6'], models=model_pairs, pre_t_min=0.7,
                                                pre_t_max=1)
    # rank bot results
    best, second_best = get_two_best_thresholds(bot_thresholds,bots_results)
    # determine alignments
    f_matches = get_matches_by_combine(activity_pairs_all, bots_results, bot_thresholds, best, second_best, model_pairs)
    # return
    to_return = {}
    for k in final_matches.keys():
        to_return[k] = final_matches[k] + f_matches[k]
    # it returns {bpmn_models_pair:list_of_matches}
    return to_return
