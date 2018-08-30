import bpmn_python.bpmn_diagram_visualizer as visualizer
import bpmn_python.bpmn_diagram_rep as diagram
import os

import metrics
import triple_s
import knoma_proc
import match_sss
import refmod_mine_nlm

import opbot

dirpath = ".\\resources\\diagrams2\\"


#Load example diagram from file
example_diagram = diagram.BpmnDiagramGraph()

example_diagram.load_diagram_from_xml_file("./resources/dataset1/models/Cologne.bpmn")
print(example_diagram)



modelFiles = os.listdir(dirpath)
# print(modelFiles)
model_name = {}
models = []
name_model = {}
#Load diagrams from files and convert them to format used by library
for f in modelFiles:
    diag = diagram.BpmnDiagramGraph()

    diag.load_diagram_from_xml_file(dirpath + f)

    models.append(diag)
    name_model[f.split('.')[0]] = diag
    model_name[diag] = f.split('.')[0]
    #simple diagram visualistion
    #visualizer.visualize_diagram(diag)


opbot_results = opbot.get_opbot_matches(name_model, opbot.get_model_pairs(name_model))
print("OPBOT RESULTS")
print(opbot_results)

for i in range(0, (len(models) - 1)):
    metrics.check_diagrams_metics(models[i], models[i + 1], True)
    triple_s_results = triple_s.get_triple_s_matches(models[i], models[i + 1], syntactic_weight=0.5, semantic_weight=0.35,
                                  ratio_weight=0.05, position_weight=0.1)
    print("TripleS")
    print(triple_s_results)
    match_sss_results = match_sss.getMatchSSSmatches(models[i], models[i + 1], 0.6)
    print("MatchSSS")
    print(match_sss_results)
    refmod_mine_nlm_results = refmod_mine_nlm.get_refmod_mine_nlm_matches(models[i], models[i + 1])
    print("RefMod-Mine/NLM")
    print(refmod_mine_nlm_results)
    knoma_proc_results= knoma_proc.get_matches(diagram1=models[i], diagram2=models[i + 1], threshold_score=3.0)
    print("KnoMaProc")
    print(knoma_proc_results)

