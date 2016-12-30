#!/usr/bin/python
# -*- coding: utf-8 -*-
# https://www.kaggle.com/c/word2vec-nlp-tutorial/details/part-3-more-fun-with-word-vectorsrint

import io
import json
import time
from os import path
from sklearn.cluster import KMeans
from gensim.models.word2vec import Word2Vec

# logging
import logging
import sys


def to_unicode(s):
    if isinstance(s, str):
        return unicode(s, 'utf-8')
    elif isinstance(s, unicode):
        return s

program = path.basename(sys.argv[0])
logger = logging.getLogger(program)
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level=logging.INFO)
logger.info("running %s" % ' '.join(sys.argv))

if len(sys.argv) < 4:
    logger.info("usage: {} <w2v_model.bin> "
                "<cluster_vol> <clusters.out>".format(sys.argv[0]))
    exit()

arguments = {"w2v_model_filepath": sys.argv[1],
             "cluster_volume": int(sys.argv[2]),
             "output_filepath": sys.argv[3]}

# Load Word2Vec model
w2v_model = Word2Vec.load(arguments["w2v_model_filepath"])

clusters_count = w2v_model.syn0.shape[0] / arguments['cluster_volume']
logger.info("Clusters count: {}".format(clusters_count))
kmeans_clustering = KMeans(n_clusters=clusters_count)

word_vectors = w2v_model.syn0[:1000]

time_start = time.time()
idx = kmeans_clustering.fit_predict(word_vectors)
time_end = time.time()
elapsed = time_end - time_start
logger.info("Time taken for K Means clustering: {} seconds.".format(elapsed))

with io.open(arguments['output_filepath'], 'w', encoding='utf-8') as out:

    # index2words returns a list words, and each word could be presented
    # as 'str' or 'unicode' string type. This leads to map all the list data
    # into list of 'unicode' strings by means of to_unicode function to avoid
    # json serialization problems.
    words = map(lambda w: to_unicode(w), w2v_model.index2word)
    result = dict(zip(words, [str(i) for i in idx]))
    data = json.dumps(result, ensure_ascii=False, indent=4)
    out.write(unicode(data))
    logger.info('Result has been saved in {}'.format(arguments[
                                                     'output_filepath']))