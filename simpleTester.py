import os
import bpmn_python.bpmn_diagram_rep as diagram
# Import algorithms
import metrics
import triple_s
import knoma_proc
import match_sss
import refmod_mine_nlm
import opbot

# Source dir for models
dirpath = ".\\resources\\diagrams2\\"
# Load example diagram from file
example_diagram = diagram.BpmnDiagramGraph()
example_diagram.load_diagram_from_xml_file("./resources/dataset1/models/Cologne.bpmn")
print(example_diagram)

modelFiles = os.listdir(dirpath)
models = []
name_model = {}  # OPBOT implementation requires dictionary {model_name:loaded_model}
# Load diagrams from files and convert them to format used by library
for f in modelFiles:
    diag = diagram.BpmnDiagramGraph()
    diag.load_diagram_from_xml_file(dirpath + f)
    models.append(diag)
    name_model[f.split('.')[0]] = diag

for i in range(0, (len(models) - 1)):
    metrics.check_diagrams_metics(models[i], models[i + 1], True)
    # To get matches from two diagrams simply pass them to algorithm function
    triple_s_results = triple_s.get_triple_s_matches(models[i], models[i + 1], syntactic_weight=0.5,
                                                     semantic_weight=0.35,
                                                     ratio_weight=0.05, position_weight=0.1)
    # Algorithm result is a list of matches
    print(triple_s_results)

    match_sss_results = match_sss.getMatchSSSmatches(diagram1=models[i], diagram2=models[i + 1], threshold=0.6)
    print(match_sss_results)

    refmod_mine_nlm_results = refmod_mine_nlm.get_refmod_mine_nlm_matches(model1=models[i], model2=models[i + 1])
    print(refmod_mine_nlm_results)

    knoma_proc_results = knoma_proc.get_matches(diagram1=models[i], diagram2=models[i + 1], threshold_score=3.0)
	print(knoma_proc_results)

# OPBOT works a little different
# OPBOT works on collection of models
opbot_results = opbot.get_opbot_matches(name_model, opbot.get_model_pairs(name_model))
# OPBOT return object is a dictionary, {bpmn_models_pair:list_of_matches}
print(opbot_results)
