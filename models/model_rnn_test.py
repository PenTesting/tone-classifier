#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import json
import logging
import zipfile
import pandas as pd
import numpy as np

import utils
import configs
from core.features import Features
from core.DocVocabulary import DocVocabulary
from core.TermVocabulary import TermVocabulary
from core.msg import TwitterMessageParser

from model_rnn import get_model_paths, get_problem

# Word embeddnig models
from model_w2v import vectorizer as w2v_vectorizer
from model_features_only import vectorizer as features_only

# Neural network models
from networks.theano.rnn import RNNTheano


def predict(model, X, sentiment_columns, result_table):
    """
        model : networks.*
            neural network model
        X : np.ndarray
            represents input sentences
        sentiment_columns : list
            list of the column names which should be filled with the sentiment
            values
        result_table : str
            output table which should be filled with the predicted result
    """
    logging.info("Predicting ...")
    y = model.forward_propagation(X)[0]

    import ipdb; ipdb.set_trace() # BREAKPOINT

    # TODO: remove duplicated code at predict.py
    logging.info("Filling answers in {} ...".format(result_table))
    df = pd.read_csv(result_table, sep=',')
    for msg_index, row_index in enumerate(df.index):
        label = np.argmax(y[msg_index]) - 1
        for column in sentiment_columns:
            if not df[column].isnull()[row_index]:
                df.set_value(row_index, column, label)

    # Rewriting table with the filled results
    df.to_csv(result_table, sep=',')
    pass


def test_network(vectorizer, network_type, task_type, test_table,
                 result_table):
    """
        result_table : str
            output filepath
    """
    paths = get_model_paths(task_type, network_type, SETTING_NAME)
    logging.info("Reading: {} ...".format(paths['embedding_output']))

    with zipfile.ZipFile(paths['embedding_output'], "r") as zf:
        logging.info("Reading: {} ...".format(configs.FEATURES_FILENAME))
        features_settings = json.loads(
            zf.read(configs.FEATURES_FILENAME), encoding='utf-8')

        logging.info("Reading: {} ...".format(
            configs.TWITTER_MESSAGE_PARSER_FILENAME))
        message_settings = json.loads(
            zf.read(configs.TWITTER_MESSAGE_PARSER_FILENAME), encoding='utf-8')

    logging.info("Reading: {} ...".format(paths['model_output']))
    model = NETWORKS[network_type].load(paths['model_output'])

    features = Features(
        TwitterMessageParser(message_settings, task_type),
        features_settings)

    term_vocabulary = TermVocabulary()
    doc_vocabulary = DocVocabulary()

    problem = utils.create_problem(task_type,
                                   'test',
                                   test_table,
                                   vectorizer,
                                   features,
                                   term_vocabulary,
                                   doc_vocabulary,
                                   message_settings)

    X, embedding_size = get_problem(problem, get_results=False)

    logging.info('Create a file for classifier results: {}'.format(
            result_table))
    result_df = pd.read_csv(test_table, sep=',')
    result_df.to_csv(result_table, sep=',')

    predict(model, X, utils.get_score_columns(task_type), result_table)


if __name__ == "__main__":

    VECTORIZERS = {
            'w2v': w2v_vectorizer,
            'features_only': features_only
        }

    NETWORKS = {
            'rnn': RNNTheano,
            'lstm': None,
            'gru': None
        }

    utils.init_logger()
    config = {'setting_name': sys.argv[1],
              'vectorizer_type': sys.argv[2],
              'network_type': sys.argv[3],
              'task_type': sys.argv[4],
              'test_table': sys.argv[5],
              'model_out': sys.argv[6]}

    SETTING_NAME = config['setting_name']

    test_network(
            VECTORIZERS[config['vectorizer_type']],
            config['network_type'],
            config['task_type'],
            config['test_table'],
            config['model_out'])
