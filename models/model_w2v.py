#!/usr/bin/python
# -*- coding: utf-8 -*-

# global
import io
import os
import json
import logging
from gensim.models.word2vec import Word2Vec
import numpy as np

# this
import utils
import model_features_only

# configs
import configs


def vectorizer(labeled_message, term_voc, doc_voc):
    """
    Vector builder

    Arguments:
    ---------
        labeled_message -- dictionary with the following fields:
                           {score, id, terms, features}
        term_voc -- vocabulary of terms
        doc_voc -- vocabulary of documents

    Returns
    ------
        vector -- {index1: value1, ... , indexN: valueN}
    """
    features = labeled_message['features']
    vector = model_features_only.feature_vectorizer(features, term_voc)

    terms = labeled_message['terms']
    for model_index, w2v_model in enumerate(W2V_MODELS):
        w2v_vector = w2v_vectorizer(terms, term_voc, w2v_model, model_index)
        vector.update(w2v_vector)

    return vector


def w2v_vectorizer(terms, term_voc, w2v_model, model_index):
    """
    Produces the vector of terms, which is based on vectors from word2vec
    model.

    Arguments
    ---------
        terms -- list of terms
        term_voc -- vocabulary of terms
        w2v_model -- Word2Vec model, which is used to extract vectors for each
        term
        model_index -- used to generate unique term name and save it in
        vocabulary of terms

    Returns
    ------
        vector -- {index1: value1, ..., indexN: valueN}
    """
    vector = {}

    union_type = CONFIG_WORD2VEC_UNIONTYPE

    if (union_type == configs.W2V_UNIONTYPE_SUM):
        w2v_vector = sum_w2v_vectors(w2v_model, terms)
    elif (union_type == configs.W2V_UNIONTYPE_CONCAT):
        w2v_vector = concat_w2v_vectors(w2v_model, terms)
    else:
        raise Exception("union type '%s' doesn't suppport" % (union_type))

    term_voc.insert_terms([index2term(model_index, item_index)
                           for item_index in range(0, w2v_vector.size)])

    for w2v_index, w2v_value in enumerate(w2v_vector):
        term = index2term(model_index, w2v_index)
        index = term_voc.insert_term(term)
        vector[index] = w2v_value

    return vector


def sum_w2v_vectors(w2v_model, terms, calculate_middle=False):
    """
    Sum all vectors from Word2Vec model for all terms presented in model
    """
    w2v_vector = np.array([0] * w2v_model.vector_size, dtype=np.float32)
    used_terms_count = 0
    for term in terms:
        if term in w2v_model:
            used_terms_count += 1
            w2v_vector = w2v_vector + w2v_model[term]

    if calculate_middle is True:
        if used_terms_count > 0:
            w2v_vector = w2v_vector / used_terms_count

    return w2v_vector


def concat_w2v_vectors(w2v_model, terms, limit=5):
    """
    Concatenate vectors from Word2Vec model for first 'limit' terms, presented
    in model
    """
    vectors = [w2v_model[term] for term in terms if term in w2v_model][:limit]
    if len(vectors) < limit:
        for i in range(limit-len(vectors)):
            vectors.append(np.zeros(w2v_model.vector_size))

    return np.concatenate(vectors)


def index2term(model_index, item_index):
    return '$W2V_ITEM_{model}_{item}'.format(model=str(model_index),
                                             item=str(item_index))


utils.init_logger()

with io.open(configs.W2V_CONFIG, 'r') as f:
    config = json.load(f, encoding='utf-8')

CONFIG_WORD2VEC_MODELS = "w2v_models"
CONFIG_WORD2VEC_UNIONTYPE = config["union_type"]

W2V_MODELS = []
for model in config[CONFIG_WORD2VEC_MODELS]:
        model_params = config[CONFIG_WORD2VEC_MODELS][model]
        if model_params['enabled'] == 'true':
            model_path = os.path.join(
                os.path.dirname(configs.DATA_ROOT), model_params['path'])
            logging.info("Loading Word2Vec model: {} ...".format(model_path))
            W2V_MODELS.append(Word2Vec.load_word2vec_format(model_path))

if __name__ == "__main__":
    utils.vectorization_core(vectorizer, init_term_vocabulary=False)
