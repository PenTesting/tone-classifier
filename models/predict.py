#!/usr/bin/python

# global
import sys
import json
import logging
import pandas as pd
import utils
from inspect import getsourcefile
from os.path import abspath, dirname
# -----------------------------------------------------------------------------
LIBSVM_PATH = '/classifiers/libsvm/python'
sys.path.insert(0, dirname(abspath(getsourcefile(lambda: 0)))+LIBSVM_PATH)
LIBLINEAR_PATH = '/classifiers/liblinear/python'
sys.path.insert(0, dirname(abspath(getsourcefile(lambda: 0)))+LIBLINEAR_PATH)
# -----------------------------------------------------------------------------
import svmutil
import liblinearutil


def predict(lib_type, problem_filepath, model_filepath):
    if (lib_type == 'svm'):
        ids, p_label = svm_predict(problem_filepath, model_filepath)
    elif (lib_type == 'liblinear'):
        ids, p_label = liblinear_predict(problem_filepath, model_filepath)
    else:
        raise ValueError("library '{}' does not support".format(lib_type))

    logging.info("-1: %s (%s%%)" % (p_label.count(-1),
                             p_label.count(-1) * 100.0 / len(p_label)))
    logging.info("0: %s (%s%%)" % (p_label.count(0),
                            p_label.count(0) * 100.0 / len(p_label)))
    logging.info("1: %s (%s%%)" % (p_label.count(1),
                            p_label.count(1) * 100.0 / len(p_label)))

    return (ids, p_label)


def liblinear_predict(problem_filepath, model_filepath):
    """
    Using LibLinear to predict result of a problem

    Returns
    -------
        (ids, labels)
    """

    # Reading a problem
    ids, x = liblinearutil.svm_read_problem(problem_filepath)

    print "len(x) = ", len(x)

    # Preparing a model
    model = liblinearutil.load_model(model_filepath)

    # Predicting
    y = [-2] * len(x)
    p_label, p_acc, p_val = liblinearutil.predict(y, x, model)

    return (ids, p_label)


def svm_predict(problem_filepath, model_filepath):
    """
    Using LibSVM to predict result of a problem

    Returns
    -------
        (ids, labels)
    """

    # Reading a problem
    ids, x = svmutil.svm_read_problem(problem_filepath)

    print "len(x) = ", len(x)

    # Preparing a model
    model = svmutil.svm_load_model(model_filepath)

    # Predicting
    y = [-2] * len(x)
    p_label, p_acc, p_val = svmutil.svm_predict(y, x, model)

    return (ids, p_label)


if len(sys.argv) == 1:
    print "%s\n%s\n%s\n%s\n%s" % (
        "usage:./%s <problem_file> <model_file> <config_file>" % (sys.argv[0]),
        "<library_type> -- available 'svm', 'liblinear'",
        "<problem_file> -- file with a problem to predict",
        "<model_file> -- file with a SVM model",
        "<config_file> -- .pconf file in model folder",
        "<out_file> -- output file")
    exit(0)

utils.init_logger()

arguments = {'library_type': sys.argv[1],
             'problem_file': sys.argv[2],
             'model_file': sys.argv[3],
             'config_file': sys.argv[4],
             'out_file': sys.argv[5]}

with open(arguments['config_file']) as f:
    config = json.load(f)

# Predict
ids, p_label = predict(arguments['library_type'],
                       arguments['problem_file'],
                       arguments['model_file'])

# Filling answers
logging.info("Filling answers in {} ...".format(config['prediction_table']))
df = pd.read_csv(config['prediction_table'], sep=',')
for msg_index, row_index in enumerate(df.index):
    label = p_label[msg_index]
    for column in config['columns']:
        if not df[column].isnull()[row_index]:
            df.set_value(row_index, column, label)

# Save
df.to_csv(arguments['out_file'], sep=',')
