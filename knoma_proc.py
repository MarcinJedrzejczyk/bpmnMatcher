# -*- coding: utf-8 -*-
from __future__ import division
import math
import commonFunctions as cf
import lucene
import matcher
from org.apache.lucene import analysis, document, index, queryparser, search, store
from lupyne import engine

activeComponents = ['task', 'event']

MAIN_INDEX_DIR = "./indexes"


def transform_to_index(my_nodes):
    to_return = []

    for n in my_nodes:
        doc = document.Document()

        doc.add(document.Field("id", n.id, document.TextField.TYPE_STORED))
        doc.add(document.Field("label", " ".join(n.label), document.TextField.TYPE_STORED))
        for el in n.inputlabel:
            doc.add(document.Field("next", " ".join(el), document.TextField.TYPE_STORED))
        for el in n.outputlabel:
            doc.add(document.Field("prev", " ".join(el), document.TextField.TYPE_STORED))

        to_return.append(doc)

    return to_return


def create_index(directory, analyzer, documents_to_index):
    config = index.IndexWriterConfig(analyzer)
    index_writer = index.IndexWriter(directory, config)
    for doc in documents_to_index:
        index_writer.addDocument(doc)

    index_writer.close()


def create_query(entity, parser):
    query_text = "label:\"" + " ".join(entity.label) + "\""

    for el in entity.inputlabel:
        query_text = query_text + " OR  next:\"" + " ".join(el) + "\""

    for el in entity.outputlabel:
        query_text = query_text + " OR prev:\"" + " ".join(el) + "\""
    return parser.parse(query_text)


def get_temp_matches(entity, hits, index_searcher):
    to_return = []

    for hit in hits:
        hit_doc = index_searcher.doc(hit.doc)
        to_return.append(temp_match(id1=entity.id, id2=hit_doc['id'], score=hit.score))

    return to_return


def search_index(directory_to_search, entities_to_check, analyzer):
    to_return = {}

    index_reader = index.DirectoryReader.open(directory_to_search)
    index_searcher = search.IndexSearcher(index_reader)
    parser = queryparser.classic.QueryParser("label", analyzer)
    for entity in entities_to_check:
        query = create_query(entity, parser)
        hits = index_searcher.search(query, 1000).scoreDocs
        to_return[entity] = get_temp_matches(entity, hits, index_searcher)

    index_reader.close()
    return to_return


def get_matches(diagram1, diagram2, threshold_score=3.0, consider_context=True):
    # initVM for lucene
    lucene.initVM()

    # index creation
    p1 = get_preprocessed_nodes(diagram1, consider_context)
    p2 = get_preprocessed_nodes(diagram2, consider_context)

    docs_from_p1 = transform_to_index(p1)
    docs_from_p2 = transform_to_index(p2)

    # set up in memory store for indexes
    directory1 = store.RAMDirectory()
    directory2 = store.RAMDirectory()
    analyzer = analysis.standard.StandardAnalyzer()

    # create separate indexes for each diagram
    create_index(directory=directory1, analyzer=analyzer, documents_to_index=docs_from_p1)
    create_index(directory=directory2, analyzer=analyzer, documents_to_index=docs_from_p2)

    # SEARCH STEP: use indexes from one store to search on indexes from other store
    res_1 = search_index(directory_to_search=directory2, entities_to_check=p1, analyzer=analyzer)
    res_2 = search_index(directory_to_search=directory1, entities_to_check=p2, analyzer=analyzer)

    # apply match search pruning rules
    set_m = prune_results(res_1, res_2, threshold_score)

    directory1.close()
    directory2.close()
    return set_m


def get_two_best(list_of_matches):
    if list_of_matches.__eq__([]) or list_of_matches is None:
        return []

    sp = sorted(list_of_matches, key=lambda x: x.score, reverse=True)
    if sp.__len__() == 1:
        return sp
    elif sp.__len__() > 1:
        return [sp[0], sp[1]]
    else:
        return []


def prune_results(res_1, res_2, threshold=3.0):
    to_return = set()
    res_1_all_values = []
    for value in res_1.values():
        res_1_all_values = res_1_all_values + value

    res_2_all_values = []
    for value in res_1.values():
        res_2_all_values = res_2_all_values + value

    for entity in res_1.keys():
        do_rule_3 = res_1[entity].__len__()
        for match in res_1[entity]:
            # RULE 1
            if res_1_all_values.__contains__(match) and res_2_all_values.__contains__(match):
                to_return.add(
                    matcher.match(node1=entity.node, node2=get_node_from_entities(match.id2, res_2.keys()), score=1.0))
            # RULE 2
            elif res_1_all_values.__contains__(match) or res_2_all_values.__contains__(match):
                if match.score >= threshold:
                    to_return.add(
                        matcher.match(node1=entity.node, node2=get_node_from_entities(match.id2, res_2.keys()),
                                      score=1.0))
            else:
                do_rule_3 = do_rule_3 - 1
        # RULE 3
        if do_rule_3 == 0:
            for match in get_two_best(res_1[entity]):
                to_return.add(
                    matcher.match(node1=entity.node, node2=get_node_from_entities(match.id2, res_2.keys()), score=1.0))

    for entity in res_2.keys():
        do_rule_3 = res_2[entity].__len__()
        for match in res_2[entity]:
            # RULE 1
            if res_1_all_values.__contains__(match) and res_2_all_values.__contains__(
                    match):
                to_return.add(
                    matcher.match(node1=entity.node, node2=get_node_from_entities(match.id2, res_1.keys()), score=1.0))
            # RULE 2
            elif res_1_all_values.__contains__(match) or res_2_all_values.__contains__(match):
                if match.score >= threshold:
                    to_return.add(
                        matcher.match(node1=entity.node, node2=get_node_from_entities(match.id2, res_1.keys()),
                                      score=1.0))
            else:
                do_rule_3 = do_rule_3 - 1
        # RULE 3
        if do_rule_3 == 0:
            for match in get_two_best(res_2[entity]):
                to_return.add(
                    matcher.match(node1=entity.node, node2=get_node_from_entities(match.id2, res_1.keys()), score=1.0))

    return to_return


def get_preprocessed_nodes(process, consider_context=True):
    entities = []
    for node in cf.get_nodes(process, activeComponents, True):
        node_name = node['id']
        # nodeName is an id of node in diagram(key in dictionary)
        out_labels = []
        in_labels = []

        for labelId in process.diagram_graph.node[node_name]['outgoing']:
            _, _, isa = process.get_flow_by_id(labelId)
            out_labels.append(process.diagram_graph.node[isa['targetRef']]['node_name'])

        for labelId in process.diagram_graph.node[node_name]['incoming']:
            _, _, isa = process.get_flow_by_id(labelId)
            in_labels.append(process.diagram_graph.node[isa['sourceRef']]['node_name'])

        final_label = cf.lemminisation(cf.get_tokens(process.diagram_graph.node[node_name]['node_name'].lower()))
        if consider_context:
            final_in_labels = []
            final_out_labels = []

            for label in in_labels:
                if not label.__eq__(""):
                    final_in_labels.append(cf.lemminisation(cf.get_tokens(label.lower())))
            for label in out_labels:
                if not label.__eq__(""):
                    final_out_labels.append(cf.lemminisation(cf.get_tokens(label.lower())))

            index_en = indexEntity(process.diagram_graph.node[node_name], process.diagram_graph.node[node_name]['id'],
                                   final_label, final_in_labels,
                                   final_out_labels)
            entities.append(index_en)
        else:
            index_en = indexEntity(process.diagram_graph.node[node_name], process.diagram_graph.node[node_name]['id'],
                                   final_label, [], [])
            entities.append(index_en)

    return entities


def get_node_from_entities(node_id, entities_list):
    for item in entities_list:
        if item.id == node_id:
            return item.node
    return None


class temp_match:
    def __init__(self, id1, id2, score):
        self.id1 = id1
        self.id2 = id2
        self.score = score

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self.id1.__eq__(getattr(other, 'id1')) and self.id2.__eq__(getattr(other, 'id2')):
                return True
            elif self.id1.__eq__(getattr(other, 'id2')) and self.id2.__eq__(getattr(other, 'id1')):
                return True
            else:
                return False
        else:
            return False

    def __hash__(self):
        return hash(self.id1) + hash(self.id2)


class indexEntity():
    def __init__(self, node, name, label, inLabel, outLabel):
        '''

        :param name: node id in diagram
        :param label: label text
        :param inLabel: list of list, each list consist of tokenised input label after lemmatisation
        :param outLabel: list of list, each list consist of tokenised input label after lemmatisation
        '''
        self.node = node
        self.id = name
        self.label = label
        self.inputlabel = inLabel
        self.outputlabel = outLabel

    def __str__(self):
        return "\n id:{}\n label:{} \ninput labels:{}\n output labels:{}\n ".format(self.id, self.label,
                                                                                    self.inputlabel, self.outputlabel)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                getattr(other, 'id', None) == self.id and
                getattr(other, 'label', None) == self.label and
                getattr(other, 'inputlabel', None) == self.inputlabel and
                getattr(other, 'outputlabel', None) == self.outputlabel
                )

    def __hash__(self):
        return hash(self.id) + hash(" ".join(self.label))
