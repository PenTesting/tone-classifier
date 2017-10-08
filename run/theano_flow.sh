#!/bin/bash

rm ../data/networks/models/*

# test for 'twitter_10m_300' model
../models/w2v_api.py all 0
../models/w2v_api.py twitter_10m_300 1
../models/features_api.py lexicons all 0
make theano-lstm-1l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-2l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-1l_diagnostic_sre16_tcc_w2v_imb
make theano-lstm-2l_diagnostic_sre16_tcc_w2v_imb

../models/features_api.py lexicons feb_june_16_lexicon
make theano-lstm-1l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-2l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-1l_diagnostic_sre16_tcc_w2v_imb
make theano-lstm-2l_diagnostic_sre16_tcc_w2v_imb

../models/features_api.py lexicons mtd_rus_lexicon
make theano-lstm-1l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-2l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-1l_diagnostic_sre16_tcc_w2v_imb
make theano-lstm-2l_diagnostic_sre16_tcc_w2v_imb

../models/features_api.py lexicons rubtsova_lexicon
make theano-lstm-1l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-2l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-1l_diagnostic_sre16_tcc_w2v_imb
make theano-lstm-2l_diagnostic_sre16_tcc_w2v_imb

../models/features_api.py lexicons experts_lexicon
make theano-lstm-1l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-2l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-1l_diagnostic_sre16_tcc_w2v_imb
make theano-lstm-2l_diagnostic_sre16_tcc_w2v_imb

# Two vocabularies
../models/w2v_api.py banks_300 1
../models/features_api.py lexicons all 0
make theano-lstm-1l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-2l_diagnostic_sre16_bank_w2v_imb

../models/features_api.py lexicons feb_june_16_lexicon
make theano-lstm-1l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-2l_diagnostic_sre16_bank_w2v_imb

../models/features_api.py lexicons mtd_rus_lexicon
make theano-lstm-1l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-2l_diagnostic_sre16_bank_w2v_imb

../models/features_api.py lexicons rubtsova_lexicon
make theano-lstm-1l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-2l_diagnostic_sre16_bank_w2v_imb

../models/features_api.py lexicons experts_lexicon
make theano-lstm-1l_diagnostic_sre16_bank_w2v_imb
make theano-lstm-2l_diagnostic_sre16_bank_w2v_imb
