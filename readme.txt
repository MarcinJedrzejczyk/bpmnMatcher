The aim of this project was to implement chosen algorithms from ''The Process Model Matching Contest 2015'' in Python. 
These algorithms are used to compare business process diagrams, to find elements that are similar.

The libraries used in runtime environment are listed in file libraries.PNG and in setup.py file.

The file simpleTester.py is an example of usage of this module. How to use each algorithm code to get matches,
how to load bpmn file and how to see metrics for two diagrams.

The file evaluator.py create results that can be compared with ''The Process Model Matching Contest 2015'' results.
However you need to choose algorithm and in RefMod-Mine/NLM case you need to choose fragment of data(it takes to long to simply
run it on whole data set). Results will be stored in ''results'' dir.