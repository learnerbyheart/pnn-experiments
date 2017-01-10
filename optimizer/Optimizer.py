import OptimizedModels
import random
from parameters import parameter_space
from logs import Logger
import config

max_evals = config.number_of_evals

for model_nr in xrange(max_evals):
    params = {}
    for key, values in parameter_space.space.iteritems():
        params[key] = random.choice(values)

    print "Model nr. ", model_nr
    #model_pos, best_dev_scores_pos, best_test_scores_pos = OptimizedModels.getPOSModel(params)
    #model_ner, best_dev_scores_ner, best_test_scores_ner = OptimizedModels.getNERModel(params)
    best_dev_scores_chunking, best_test_scores_chunking = OptimizedModels.getChunkingModel(params)
    print params
    '''for score in best_dev_scores_pos:
        print "Max acc dev pos: %.4f in epoch: %d" % (score[0], score[1])
        Logger.save_results(config.optimized_models_log_path, 'pos', 'dev', params, score[0], score[1])
    for score in best_test_scores_pos:
        print "Max acc test pos: %.4f in epoch: %d" % (score[0], score[1])
        Logger.save_results(config.optimized_models_log_path, 'pos', 'test', params, score[0], score[1])
    for score in best_dev_scores_ner:
        print "Max f1 dev ner: %.4f in epoch: %d" % (score[0][2], score[1])
        Logger.save_results(config.optimized_models_log_path, 'ner', 'dev', params, score[0][2], score[1])
    for score in best_test_scores_ner:
        print "Max f1 test ner: %.4f in epoch: %d" % (score[0][2], score[1])
        Logger.save_results(config.optimized_models_log_path, 'ner', 'test', params, score[0][2], score[1])'''
    for score in best_dev_scores_chunking:
        print "Max f1 dev chunking: %.4f in epoch: %d" % (score[0][2], score[1])
        Logger.save_results(config.optimized_models_log_path, 'ner', 'dev', params, score[0][2], score[1])
    for score in best_test_scores_chunking:
        print "Max f1 test chunking: %.4f in epoch: %d" % (score[0][2], score[1])
        Logger.save_results(config.optimized_models_log_path, 'ner', 'test', params, score[0][2], score[1])

