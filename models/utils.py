# -*- coding: utf-8 -*-

# global
import sys
import json
import psycopg2

# core
import core
import core.utils
import core.indexer
from core.DocVocabulary import DocVocabulary
from core.TermVocabulary import TermVocabulary
from core.features import Features
from core.msg import TwitterMessageParser

# configs
import configs

TTK_TASK = 'ttk'
BANK_TASK = 'bank'


def vectorization_core(vectorizer, init_term_vocabulary=True,
                       merge_doc_vocabularies=False):
    """
    Main function of collection vectorization

    vectorizer : message vectorization function
    returns : None
    """
    if (sys.argv < 8):
        exit(0)

    config = {'task_type': sys.argv[1],
              'database': sys.argv[2],
              'train_table': sys.argv[3],
              'test_table': sys.argv[4],
              'train_output': sys.argv[5],
              'test_output': sys.argv[6],
              'pconf_output': sys.argv[7]}
    message_configpath = configs.TWITTER_MESSAGE_PARSER_CONFIG
    features_configpath = configs.FEATURES_CONFIG

    # Connect to a database
    connectionSettings = "dbname=%s user=%s password=%s host=%s" % (
                                config['database'],
                                configs.CONNECTION_SETTINGS['user'],
                                configs.CONNECTION_SETTINGS['password'],
                                configs.CONNECTION_SETTINGS['host'])
    connection = psycopg2.connect(connectionSettings)

    # Create vocabulary of terms
    if init_term_vocabulary is True:
        term_vocabulary = core.indexer.create_term_vocabulary(
                                connection,
                                [config['train_table'], config['test_table']],
                                message_configpath)
    else:
        term_vocabulary = TermVocabulary()

    features = Features(
                connection,
                TwitterMessageParser(message_configpath, config['task_type']),
                features_configpath)

    doc_vocabulary = DocVocabulary()
    # Train problem
    train_problem = create_problem(connection,
                                   config['task_type'],
                                   'train',
                                   config['train_table'],
                                   vectorizer,
                                   features,
                                   term_vocabulary,
                                   doc_vocabulary,
                                   features_configpath,
                                   message_configpath)

    if not merge_doc_vocabularies:
        doc_vocabulary = DocVocabulary()
    # Test problem
    test_problem = create_problem(connection,
                                  config['task_type'],
                                  'test',
                                  config['test_table'],
                                  vectorizer,
                                  features,
                                  term_vocabulary,
                                  doc_vocabulary,
                                  features_configpath,
                                  message_configpath)

    result_table = config['test_table'] + '_problem'
    core.utils.drop_table(connection, result_table)
    core.utils.create_table_as(connection, config['test_table'], result_table)

    # Save
    save_problem(train_problem, config['train_output'])
    save_problem(test_problem, config['test_output'])
    save_predict_config(config['database'],
                        get_score_columns(config['task_type']),
                        result_table,
                        config['pconf_output'])


def create_problem(connection, task_type, collection_type, table, vectorizer,
                   features, term_vocabulary, doc_vocabulary,
                   features_configpath, message_configpath):
    """
    Creates problem (vectors from messages with additional features)

    Arguments:
    ---------
        connection -- pgsql connection
        task_type -- BANK_TASK or 'tkk' according to SentiRuEval competiiton
        collection_type -- could be 'train' or 'test', it affects on the
                           generated vector prefixes (tone score for 'train'
                           task, and 'id' for 'test' task respectively)
        table -- table name
        vectorizer -- function for producing vector from terms
        features -- object of Features class
        term_vocabulary -- vocabulary of terms
        features_configpath -- configuration path for Features class
        messsage_configpath -- configuration path for TwitterMessageParser

    Returns:
    --------
        problem -- list of vectorized messages
    """
    message_parser = TwitterMessageParser(message_configpath, task_type)
    limit = sys.maxint
    labeled_messages = []

    for score in [-1, 0, 1]:
        print "Class:\t%s" % (score)
        # getting tweets with the same score
        request = tweets_filter_sql_request(task_type, table, score, limit)
        for row in core.utils.table_iterate(connection, request):
            text = row[0]
            index = row[1]

            message_parser.parse(text)
            terms = message_parser.get_terms()
            doc_vocabulary.add_doc(terms, str(score))
            labeled_message = {'score': score,
                               'id': index,
                               'terms': to_unicode(terms),
                               'features': features.vectorize(text)}
            labeled_messages.append(labeled_message)

            term_vocabulary.insert_terms(
                    labeled_message['features'].iterkeys())

    # Create vectors
    problem = []
    for labeled_message in labeled_messages:
        vector = vectorizer(labeled_message, term_vocabulary, doc_vocabulary)
        if (collection_type == 'train'):
            problem.append([labeled_message['score'], vector])
        elif (collection_type == 'test'):
            problem.append([labeled_message['id'], vector])
        else:
            raise ValueError(
                    'Unexpected collection_type={}'.format(collection_type))

    return problem


def get_score_columns(task_type):
    return configs.DATA_TCC_FIELDS if task_type == TTK_TASK else \
        configs.DATA_BANK_FIELDS


def to_unicode(terms):
    """
    Converts list of 'str' into list of 'unicode' strings
    """
    unicode_terms = []
    for term in terms:
        if (isinstance(term, str)):
            unicode_terms.append(unicode(term, 'utf-8'))
        else:
            unicode_terms.append(term)

    return unicode_terms


def save_problem(problem, filepath):
    """
    Save problem using the format, supported by classifier libraries
    """
    with open(filepath, "w") as out:
        print "Vectors count: %s" % (len(problem))
        for vector in problem:
            out.write("%s " % (vector[0]))
            for index, value in sorted(vector[1].iteritems()):
                out.write("%s:%s " % (index, value))
            out.write("\n")


def tweets_filter_sql_request(task_type, table, score, limit):
    """
    task_type: TTK_TASK or BANK_TASK
        string, name of the task
    """
    if (task_type == BANK_TASK):
        return "SELECT text, id, sberbank, vtb, gazprom, alfabank, "\
               "bankmoskvy, raiffeisen, uralsib, rshb FROM %s WHERE "\
               "(sberbank=\'%d\' OR vtb=\'%d\' OR gazprom=\'%d\' OR "\
               "alfabank=\'%d\' OR bankmoskvy=\'%d\' OR raiffeisen=\'%d\' "\
               "OR uralsib=\'%d\' OR rshb=\'%d\') "\
               "LIMIT(\'%d\');" % (table, score, score, score, score, score,
                                   score, score, score, limit)
    elif (task_type == TTK_TASK):
        return "SELECT text, id, beeline, mts, megafon, tele2, "\
               "rostelecom, komstar, skylink FROM %s WHERE "\
               "(beeline=\'%d\' OR mts=\'%d\' OR megafon=\'%d\' "\
               "OR tele2=\'%d\' OR rostelecom=\'%d\' OR komstar=\'%d\' "\
               "OR skylink=\'%d\') LIMIT(\'%d\')" % (table, score, score,
                                                     score, score, score,
                                                     score, score, limit)


def save_predict_config(database, columns, prediction_table, out_filepath):
    config = {"database": database,
              "columns": columns,
              "prediction_table": prediction_table}

    with open(out_filepath, "w") as out:
        json.dump(config, out)
