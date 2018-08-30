# -*- coding: utf-8 -*-
from __future__ import division
import bpmn_python.bpmn_diagram_rep as diagram
import os
import csv
import datetime
import uuid
import match_sss
import knoma_proc
import triple_s
import opbot
import refmod_mine_nlm
import matcher


def get_models_names_from_gs_files(dir_path):
    pairs = []
    for filename in os.listdir(dir_path):
        split = filename.split('.')[0].split('-')
        pairs.append((split[0], split[1]))
    return pairs


if __name__ == "__main__":
    models_path = "./resources/dataset1/models"
    gold_standard_path = "./resources/dataset1/goldstandard"
    now = datetime.datetime.now()

    csv_file = './results/' + 'results ' + str(uuid.uuid4().hex) + ' .csv'
    tripleS_scores = []
    matchSSS_scores = []
    refmod_mine_scores = []
    opbot_scores = []
    knomaproc_scores = []

    #chosen_one = 'matchSSS'
    chosen_one='tripleS'
    # chosen_one='refmodmine'
    # chosen_one = 'opbot'
    # chosen_one='knomaproc'

    # load models from dataset1
    models = {}
    name_model = {}
    for file_name in os.listdir(models_path):
        diag = diagram.BpmnDiagramGraph()
        diag.load_diagram_from_xml_file(models_path + "/" + file_name)
        models[file_name.split('.')[0]] = diag
        name_model[file_name.split('.')[0]] = diag

    chosen_results = dict()
    # load pair names from gold standard
    i = 0

    if chosen_one == 'opbot':

        models_pairs = opbot.get_model_pairs(name_model)

        for k in range(0, 36, 3):
            print('iteration:' + str(k))
            part_of_pairs = list(models_pairs)[k:(k + 3)]
            part_of_name_model = opbot.get_models_from_pairs(part_of_pairs)

            opbot_match_temp = opbot.get_opbot_matches(dataset=part_of_name_model, model_pairs=part_of_pairs)
            # {model_pair:[matcher.match]}
            for pair in opbot_match_temp.keys():
                m1 = pair.model1
                m2 = pair.model2
                gold_file = gold_standard_path + "\\" + m1 + "-" + m2 + ".rdf"

                if not matcher.check_file(gold_file):
                    m1 = pair.model2
                    m2 = pair.model1
                    gold_file = gold_standard_path + "\\" + m1 + "-" + m2 + ".rdf"

                gold = matcher.load_gold_standard(gold_file)
                opbot_match = [matcher.match_into_gold_match(x, m1, m2, models[m1], models[m2]) for x in
                               opbot_match_temp[pair]]
                opbot_scores.append(matcher.check_gold_standard(matching=opbot_match, gold_standard=gold))
                chosen_results[m1 + '-' + m2] = matcher.check_gold_standard(matching=opbot_match, gold_standard=gold)
    else:
        j = 38

        for m1, m2 in get_models_names_from_gs_files(gold_standard_path):
            i += 1
            gold_file = gold_standard_path + "\\" + m1 + "-" + m2 + ".rdf"

            gold = matcher.load_gold_standard(gold_file)
            print('{}={}'.format(m1, m2))
            if chosen_one == 'tripleS':
                temp = triple_s.get_triple_s_matches(bpmn1=models[m1], bpmn2=models[m2], syntactic_weight=0.5,
                                                     semantic_weight=0.35, ratio_weight=0.0375, position_weight=0.1125,
                                                     threshold=0.7)
                triple_match = [matcher.match_into_gold_match(x, m1, m2, models[m1], models[m2], score_to_one=True) for
                                x in temp]
                tripleS_scores.append(matcher.check_gold_standard(matching=triple_match, gold_standard=gold))
                chosen_results[m1 + '-' + m2] = matcher.check_gold_standard(matching=triple_match, gold_standard=gold)

            if chosen_one == 'matchSSS':
                matchSSS_match_temp = match_sss.getMatchSSSmatches(diagram1=models[m1], diagram2=models[m2],
                                                                   threshold=0.7)
                matchSSS_match = [matcher.match_into_gold_match(x, m1, m2, models[m1], models[m2], score_to_one=True)
                                  for x in matchSSS_match_temp]
                matchSSS_scores.append(matcher.check_gold_standard(matching=matchSSS_match, gold_standard=gold))
                chosen_results[m1 + '-' + m2] = matcher.check_gold_standard(matching=matchSSS_match, gold_standard=gold)

            if chosen_one == 'refmodmine' and j <= i:
                refmod_mine_match_temp = refmod_mine_nlm.get_refmod_mine_nlm_matches(model1=models[m1],
                                                                                     model2=models[m2])
                refmod_mine_match = [matcher.match_into_gold_match(x, m1, m2, models[m1], models[m2], score_to_one=True)
                                     for x in refmod_mine_match_temp]
                refmod_mine_scores.append(matcher.check_gold_standard(matching=refmod_mine_match, gold_standard=gold))
                chosen_results[m1 + '-' + m2] = matcher.check_gold_standard(matching=refmod_mine_match,
                                                                            gold_standard=gold)

            if chosen_one == 'knomaproc':
                knomaproc_match_temp = knoma_proc.get_matches(diagram1=models[m1], diagram2=models[m2],
                                                              threshold_score=3.0)
                knomaproc_match = [matcher.match_into_gold_match(x, m1, m2, models[m1], models[m2], score_to_one=True)
                                   for x in knomaproc_match_temp]
                knomaproc_scores.append(matcher.check_gold_standard(gold_standard=gold, matching=knomaproc_match))
                chosen_results[m1 + '-' + m2] = matcher.check_gold_standard(matching=knomaproc_match,
                                                                            gold_standard=gold)
            #

            if i == j + 2 and chosen_one == 'refmodmine': break

    with open(csv_file, 'wb') as csvfile:
        headers = ['algorithm', 'precision_micro', 'precision_macro', 'precision_sd', 'recall_micro', 'recall_macro',
                   'recall_sd', 'f_measure_micro', 'f_measure_macro', 'f_measure_sd']
        writer = csv.writer(csvfile, delimiter=',')

        writer.writerow(headers)
        if chosen_one == 'matchSSS':
            match_sss_brief = matcher.get_summarised_scores(matchSSS_scores)
            writer.writerow(
                ['matchsss', match_sss_brief['precision']['avg-micro'], match_sss_brief['precision']['avg-macro'],
                 match_sss_brief['precision']['sd'],
                 match_sss_brief['recall']['avg-micro'], match_sss_brief['recall']['avg-macro'],
                 match_sss_brief['recall']['sd'],
                 match_sss_brief['f_measure']['avg-micro'], match_sss_brief['f_measure']['avg-macro'],
                 match_sss_brief['f_measure']['sd']])
        if chosen_one == 'tripleS':
            triple_s_brief = matcher.get_summarised_scores(tripleS_scores)

            writer.writerow(
                ['triple_s', triple_s_brief['precision']['avg-micro'], triple_s_brief['precision']['avg-macro'],
                 triple_s_brief['precision']['sd'],
                 triple_s_brief['recall']['avg-micro'], triple_s_brief['recall']['avg-macro'],
                 triple_s_brief['recall']['sd'],
                 triple_s_brief['f_measure']['avg-micro'], triple_s_brief['f_measure']['avg-macro'],
                 triple_s_brief['f_measure']['sd']])
        if chosen_one == 'knomaproc':
            knoma_proc_brief = matcher.get_summarised_scores(knomaproc_scores)

            writer.writerow(
                ['knoma_proc', knoma_proc_brief['precision']['avg-micro'], knoma_proc_brief['precision']['avg-macro'],
                 knoma_proc_brief['precision']['sd'],
                 knoma_proc_brief['recall']['avg-micro'], knoma_proc_brief['recall']['avg-macro'],
                 knoma_proc_brief['recall']['sd'],
                 knoma_proc_brief['f_measure']['avg-micro'], knoma_proc_brief['f_measure']['avg-macro'],
                 knoma_proc_brief['f_measure']['sd']])
        if chosen_one == 'opbot':
            opbot_brief = matcher.get_summarised_scores(opbot_scores)
            writer.writerow(
                ['opbot', opbot_brief['precision']['avg-micro'], opbot_brief['precision']['avg-macro'],
                 opbot_brief['precision']['sd'],
                 opbot_brief['recall']['avg-micro'], opbot_brief['recall']['avg-macro'],
                 opbot_brief['recall']['sd'],
                 opbot_brief['f_measure']['avg-micro'], opbot_brief['f_measure']['avg-macro'],
                 opbot_brief['f_measure']['sd']])
        if chosen_one == 'refmodmine':
            refmod_mine_nlm_brief = matcher.get_summarised_scores(refmod_mine_scores)

            writer.writerow(
                ['refmod_mine_nlm', refmod_mine_nlm_brief['precision']['avg-micro'],
                 refmod_mine_nlm_brief['precision']['avg-macro'],
                 refmod_mine_nlm_brief['precision']['sd'],
                 refmod_mine_nlm_brief['recall']['avg-micro'], refmod_mine_nlm_brief['recall']['avg-macro'],
                 refmod_mine_nlm_brief['recall']['sd'],
                 refmod_mine_nlm_brief['f_measure']['avg-micro'], refmod_mine_nlm_brief['f_measure']['avg-macro'],
                 refmod_mine_nlm_brief['f_measure']['sd']])

    alg_results = './results/' + chosen_one + '   ' + str(uuid.uuid4().hex) + '.csv'

    with open(alg_results, 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        headers = ['models', 'precision', 'recall', 'f_measure', 'TP', 'FN', 'FP']
        writer.writerow(headers)

        for key, value in chosen_results.iteritems():
            writer.writerow(
                [key, value['precision'], value['recall'], value['f_measure'], value['TP'], value['FN'], value['FP']])
