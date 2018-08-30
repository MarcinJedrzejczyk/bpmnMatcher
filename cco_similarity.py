# -*- coding: utf-8 -*-
import math


class cco_occurance_similarity_calculator():
    def __init__(self, cooccurance, k):
        self.cooccurance = cooccurance
        self.k = k

    def get_top_k_indexes(self, word, k_size):

        sorted_dict = sorted(self.cooccurance[word].iterkeys(), key=(lambda key: self.cooccurance[word][key]),
                             reverse=True)

        return sorted_dict[0:k_size]

    def get_coocurence(self, wordA, wordB):
        '''

        :param wordA: word of interest
        :param wordB:
        :return: returns a count of coocurance of wordB to wordA
        '''
        return self.cooccurance[wordA][wordB]

    def get_cco_similarity(self, wordA, wordB):
        '''

        :param wordA: a string word, !!!NOT STEMMED!!!! normal word from label, only
        :param wordB: a string word, !!!NOT STEMMED!!!! normal word from label, only
        :param activity_pair:
        :return:
        '''

        def determine_sim(word1, word2):
            kwords1 = self.get_top_k_indexes(word1, self.k)
            kwords2 = self.get_top_k_indexes(word2, self.k)

            words_set = set(kwords1 + kwords2)

            return get_sim(words_set, word1, word2)

        def get_sim(words, word1, word2):
            """

            :param words: a set
            :param word1:  a string
            :param word2: a string
            :return:
            """
            vw = 0
            v = 0
            w = 0

            for word in words:
                v1 = self.get_coocurence(word1, word)
                v2 = self.get_coocurence(word2, word)

                vw += v1 * v2
                v += v1 * v1
                w += v2 * v2

            if v == 0 or w == 0:
                return 0
            else:
                return vw / math.sqrt(v * w)

        return determine_sim(wordA, wordB)


def get_coocccurance_dict(all_words, all_labels):
    cooccurance = {}
    for word in all_words:
        cooccurance[word] = dict()
        for word2 in all_words:
            cooccurance[word][word2] = 0

    for label in all_labels:
        for word in label:
            for word2 in label:
                if not word == word2:
                    cooccurance[word][word2] = cooccurance[word][word2] + 1

    return cooccurance
