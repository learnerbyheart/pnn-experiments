from logs import Logger
import config

def run_build_model(task, exp, params, build_model_func, score_name,
                    transfer_models='', transfer_config=None):
    if transfer_config is None:
        train_scores, dev_scores, test_scores = build_model_func(params)
    else:
        train_scores, dev_scores, test_scores = build_model_func(params, transfer_config)
        transfer_models = '-'.join(sorted(filter(lambda model: model not in ['words', 'casing'], transfer_config)))

    print params
    for (score, sample) in train_scores:
        print "Max {0} train {1} with {2}: {3:.4f} in epoch: {4} with samples: {5}".format(
            score_name, task, transfer_models, score[0], score[1], sample)
        Logger.save_reduced_datasets_results(
            config.experiments_log_path, exp, task, 'train', params,
            score[0], score[1], sample, transfer_models)
    for (score, sample) in dev_scores:
        print "Max {0} dev {1} with {2}: {3:.4f} in epoch: {4} with samples: {5}".format(
            score_name, task, transfer_models, score[0], score[1], sample)
        Logger.save_reduced_datasets_results(
            config.experiments_log_path, exp, task, 'dev', params,
            score[0], score[1], sample, transfer_models)
    for (score, sample) in test_scores:
        print "Max {0} test {1} with {2}: {3:.4f} in epoch: {4} with samples: {5}".format(
            score_name, task, transfer_models, score[0], score[1], sample)
        Logger.save_reduced_datasets_results(
            config.experiments_log_path, exp, task, 'test', params,
            score[0], score[1], sample, transfer_models)

    print '\n\n-------------------- END --------------------\n\n'