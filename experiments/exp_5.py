from datasets.conll_ner import CoNLLNer
from datasets.conll_chunking import CoNLLChunking
from datasets.wsj_pos import WSJPos
from embeddings.dependency_based_word_embeddings import DependencyBasedWordEmbeddings as Embeddings
from models import Trainer, InputBuilder
from models.NER import SennaNER as NER
from models.POS import SennaPOS as POS
from models.Chunking import SennaChunking as Chunking
from optimizer import OptimizedModels
from measurements import Measurer
import config
from parameters import parameter_space
from logs import Logger
import random

# settings
default_params = {
    'update_word_embeddings': False,
    'window_size': 3,
    'batch_size': 128,
    'hidden_dims': 100,
    'activation': 'tanh',
    'dropout': 0.3,
    'optimizer': 'adam'
}

number_of_epochs = config.number_of_epochs

# ----- metric results -----#

# Casing matrix
case2Idx = {'numeric': 0, 'allLower': 1, 'allUpper': 2, 'initialUpper': 3, 'other': 4, 'mainly_numeric': 5,
            'contains_digit': 6, 'PADDING': 7}
n_in_case = len(case2Idx)

# Read in embeddings
embeddings = Embeddings.embeddings
word2Idx = Embeddings.word2Idx

def buildAndTrainNERModel(learning_params=None):
    if learning_params is None:
        params = default_params
    else:
        params = learning_params

    [input_train, train_y_cat], [input_dev, dev_y], [input_test, test_y], dicts = CoNLLNer.readDataset(
        params['window_size'], word2Idx, case2Idx)

    [train_x, train_case_x] = input_train
    [dev_x, dev_case_x] = input_dev
    [test_x, test_case_x] = input_test
    [_, caseLookup, label2Idx, idx2Label] = dicts
    n_out = train_y_cat.shape[1]

    n_in_x = train_x.shape[1]
    n_in_casing = train_case_x.shape[1]

    input_layers, inputs = InputBuilder.buildStandardModelInput(embeddings, case2Idx, n_in_x, n_in_casing, params['update_word_embeddings'])

    model_pos = OptimizedModels.getPOSModelGivenInput(input_layers, inputs, window_size=params['window_size'])
    #model_chunking = OptimizedModels.getChunkingModelGivenInput(input_layers, inputs, window_size=params['window_size'])

    model_ner = NER.buildNERModelWithPNN2(input_layers, inputs, params, n_out, additional_models=[model_pos])

    # ----- Train Model ----- #
    biof1 = Measurer.create_compute_BIOf1(idx2Label)
    train_scores, dev_scores, test_scores = Trainer.trainModelWithIncreasingData(model_ner, input_train,
                                                                   train_y_cat, number_of_epochs,
                                                                   params['batch_size'], input_dev,
                                                                   dev_y, input_test, test_y,
                                                                   measurements=[biof1])

    return train_scores, dev_scores, test_scores

def buildAndTrainPOSModel(learning_params=None):
    if learning_params is None:
        params = default_params
    else:
        params = learning_params

    [input_train, train_y_cat], [input_dev, dev_y], [input_test, test_y] = WSJPos.readDataset(
        params['window_size'], word2Idx, case2Idx)

    [train_x, train_case_x] = input_train
    [dev_x, dev_case_x] = input_dev
    [test_x, test_case_x] = input_test
    n_out = train_y_cat.shape[1]

    n_in_x = train_x.shape[1]
    n_in_casing = train_case_x.shape[1]

    input_layers, inputs = InputBuilder.buildStandardModelInput(embeddings, case2Idx, n_in_x, n_in_casing, params['update_word_embeddings'])

    model_ner = OptimizedModels.getNERModelGivenInput(input_layers, inputs, window_size=params['window_size'])
    #model_chunking = OptimizedModels.getChunkingModelGivenInput(input_layers, inputs, window_size=params['window_size'])

    model_pos = POS.buildPOSModelWithPNN2(input_layers, inputs, params, n_out, additional_models=[model_ner])

    # ----- Train Model ----- #
    train_scores, dev_scores, test_scores = Trainer.trainModelWithIncreasingData(model_pos, input_train,
                                                                   train_y_cat, number_of_epochs,
                                                                   params['batch_size'], input_dev,
                                                                   dev_y, input_test, test_y,
                                                                   measurements=[Measurer.measureAccuracy])

    return train_scores, dev_scores, test_scores

def buildAndTrainChunkingModel(learning_params=None):
    if learning_params is None:
        params = default_params
    else:
        params = learning_params

    [input_train, train_y_cat], [input_dev, dev_y], [input_test, test_y], dicts = CoNLLChunking.readDataset(
        params['window_size'], word2Idx, case2Idx)

    [train_x, train_case_x] = input_train
    [dev_x, dev_case_x] = input_dev
    [test_x, test_case_x] = input_test
    [_, caseLookup, label2Idx, idx2Label] = dicts
    n_out = train_y_cat.shape[1]

    n_in_x = train_x.shape[1]
    n_in_casing = train_case_x.shape[1]

    input_layers, inputs = InputBuilder.buildStandardModelInput(embeddings, case2Idx, n_in_x, n_in_casing, params['update_word_embeddings'])

    model_pos = OptimizedModels.getPOSModelGivenInput(input_layers, inputs, window_size=params['window_size'])
    model_ner = OptimizedModels.getNERModelGivenInput(input_layers, inputs, window_size=params['window_size'])

    model_chunking = Chunking.buildChunkingModelWithPNN2(input_layers, inputs, params, n_out, additional_models=[model_pos, model_ner])

    # ----- Train Model ----- #
    biof1 = Measurer.create_compute_BIOf1(idx2Label)
    train_scores, dev_scores, test_scores = Trainer.trainModelWithIncreasingData(model_chunking, input_train,
                                                                   train_y_cat, number_of_epochs,
                                                                   params['batch_size'], input_dev,
                                                                   dev_y, input_test, test_y,
                                                                   measurements=[biof1])

    return train_scores, dev_scores, test_scores


def run_pnn_exp_with_random_params():
    max_evals = config.number_of_evals

    for model_nr in xrange(max_evals):
        params = {}
        for key, values in parameter_space.space.iteritems():
            params[key] = random.choice(values)

        print "Model nr. ", model_nr

        print params
        best_train_scores_ner, best_dev_scores_ner, best_test_scores_ner = buildAndTrainNERModel(params)
        print params
        for (sample_scores, sample) in best_train_scores_ner:
            for score in sample_scores:
                print "Max f1 train ner: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'ner', 'train', params,
                                                     score[0], score[1], sample, 'pos')
        for (sample_scores, sample) in best_dev_scores_ner:
            for score in sample_scores:
                print "Max f1 dev ner: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'ner', 'dev', params,
                                                     score[0], score[1], sample, 'pos')
        for (sample_scores, sample) in best_test_scores_ner:
            for score in sample_scores:
                print "Max f1 test ner: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'ner', 'test', params,
                                                     score[0], score[1], sample, 'pos')

        best_train_scores_pos, best_dev_scores_pos, best_test_scores_pos = buildAndTrainPOSModel(params)
        print params
        for (sample_scores, sample) in best_train_scores_pos:
            for score in sample_scores:
                print "Max acc train pos: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'pos', 'train', params,
                                                     score[0], score[1], sample, 'ner')
        for (sample_scores, sample) in best_dev_scores_pos:
            for score in sample_scores:
                print "Max acc dev pos: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'pos', 'dev', params,
                                                     score[0], score[1], sample, 'ner')
        for (sample_scores, sample) in best_test_scores_pos:
            for score in sample_scores:
                print "Max acc test pos: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'pos', 'test', params,
                                                     score[0],
                                                     score[1], sample, 'ner')

        best_train_scores_chunking, best_dev_scores_chunking, best_test_scores_chunking = buildAndTrainChunkingModel(
            params)
        print params
        for (sample_scores, sample) in best_train_scores_chunking:
            for score in sample_scores:
                print "Max f1 train chunking: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'chunking', 'train',
                                                     params,
                                                     score[0], score[1], sample, 'pos-ner')
        for (sample_scores, sample) in best_dev_scores_chunking:
            for score in sample_scores:
                print "Max f1 dev chunking: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'chunking', 'dev',
                                                     params,
                                                     score[0], score[1], sample, 'pos-ner')
        for (sample_scores, sample) in best_test_scores_chunking:
            for score in sample_scores:
                print "Max f1 test chunking: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'chunking', 'test',
                                                     params,

                                                     score[0], score[1], sample, 'pos-ner')

def run_pnn_exp_with_fixed_params():
    fixed_params = {
        'update_word_embeddings': False,
        'window_size': 3,
        'batch_size': 128,
        'hidden_dims': 100,
        'activation': 'relu',
        'dropout': 0.3,
        'optimizer': 'adam',
        'number_of_epochs': [config.number_of_epochs]
    }
    max_evals = config.number_of_evals

    for model_nr in xrange(max_evals):
        print "Model nr. ", model_nr

        best_train_scores_ner, best_dev_scores_ner, best_test_scores_ner = buildAndTrainNERModel(fixed_params)
        print fixed_params
        for (sample_scores, sample) in best_train_scores_ner:
            for score in sample_scores:
                print "Max f1 train ner: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'ner', 'train', fixed_params, score[0], score[1], sample, 'pos')
        for (sample_scores, sample) in best_dev_scores_ner:
            for score in sample_scores:
                print "Max f1 dev ner: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'ner', 'dev', fixed_params, score[0], score[1], sample, 'pos')
        for (sample_scores, sample) in best_test_scores_ner:
            for score in sample_scores:
                print "Max f1 test ner: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'ner', 'test', fixed_params, score[0], score[1], sample, 'pos')

        best_train_scores_pos, best_dev_scores_pos, best_test_scores_pos = buildAndTrainPOSModel(fixed_params)
        print fixed_params
        for (sample_scores, sample) in best_train_scores_pos:
            for score in sample_scores:
                print "Max acc train pos: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'pos', 'train', fixed_params, score[0], score[1], sample, 'ner')
        for (sample_scores, sample) in best_dev_scores_pos:
            for score in sample_scores:
                print "Max acc dev pos: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'pos', 'dev', fixed_params, score[0], score[1], sample, 'ner')
        for (sample_scores, sample) in best_test_scores_pos:
            for score in sample_scores:
                print "Max acc test pos: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'pos', 'test', fixed_params, score[0],
                                                     score[1], sample, 'ner')

        best_train_scores_chunking, best_dev_scores_chunking, best_test_scores_chunking = buildAndTrainChunkingModel(
            fixed_params)
        print fixed_params
        for (sample_scores, sample) in best_train_scores_chunking:
            for score in sample_scores:
                print "Max f1 train chunking: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'chunking', 'train',
                                                     fixed_params,
                                                     score[0], score[1], sample, 'pos-ner')
        for (sample_scores, sample) in best_dev_scores_chunking:
            for score in sample_scores:
                print "Max f1 dev chunking: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'chunking', 'dev',
                                                     fixed_params,
                                                     score[0], score[1], sample, 'pos-ner')
        for (sample_scores, sample) in best_test_scores_chunking:
            for score in sample_scores:
                print "Max f1 test chunking: %.4f in epoch: %d with samples: %d" % (score[0], sample, score[1])
                Logger.save_reduced_datasets_results(config.experiments_log_path, 'exp_5', 'chunking', 'test',
                                                     fixed_params,

                                score[0], score[1], sample, 'pos-ner')

run_pnn_exp_with_fixed_params()