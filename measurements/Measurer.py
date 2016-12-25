import numpy as np
from keras.callbacks import LambdaCallback

def createBatchCallback(model, X_dev, Y_dev, X_test, Y_test, dev_scores, test_scores):

    #def log_lambda_wrapper(model, X_dev, Y_dev, X_test, Y_test, dev_scores, test_scores):
    def log_lambda(batch, logs):
        print '\n', 'Current batch:', batch
        print 'log: ', logs
        printMetrics(model, X_dev, Y_dev, X_test, Y_test, dev_scores, test_scores)
    return LambdaCallback(on_batch_end=log_lambda)
    #return log_lambda_wrapper

def printMetrics(model, X_dev, Y_dev, X_test, Y_test, dev_scores, test_scores):
    pred_dev = model.predict(X_dev, verbose=0).argmax(axis=-1)  # Prediction of the classes
    dev_acc = np.sum(pred_dev == Y_dev) / float(len(Y_dev))
    dev_scores.append(dev_acc)
    pred_test = model.predict(X_test, verbose=0).argmax(axis=-1)  # test_case_x
    test_acc = np.sum(pred_test == Y_test) / float(len(Y_test))
    test_scores.append(test_acc)

    print "Accuracy dev: %.2f%%" % ((dev_acc * 100))
    print "Accuracy test: %.2f%%" % ((test_acc * 100))

def createBatchTrainAccCallback(train_scores):
    def log_lambda(batch, logs):
        #print '\n', 'Current batch:', batch
        #print 'log: ', logs
        train_scores.append(logs['acc'])
    return LambdaCallback(on_batch_end=log_lambda)

def measureAccuracy(predictions, dataset_y):
    return np.sum(predictions == dataset_y) / float(len(dataset_y))


def create_compute_f1(idx2Label):
    return lambda predictions, dataset_y: compute_f1(predictions, dataset_y, idx2Label)

# Method to compute the accruarcy. Call predict_labels to get the labels for the dataset
def compute_f1(predictions, dataset_y, idx2Label):
    label_y = [idx2Label[element] for element in dataset_y]
    pred_labels = [idx2Label[element] for element in predictions]

    prec = compute_BIO_precision(pred_labels, label_y)
    rec = compute_BIO_precision(label_y, pred_labels)

    f1 = 0
    if (rec + prec) > 0:
        f1 = 2.0 * prec * rec / (prec + rec);

    return prec, rec, f1


def compute_BIO_precision(guessed, correct):
    correctCount = 0
    count = 0

    idx = 0
    while idx < len(guessed):
        if guessed[idx][0] == 'B':  # A new chunk starts
            count += 1

            if guessed[idx] == correct[idx]:
                idx += 1
                correctlyFound = True

                while idx < len(guessed) and guessed[idx][0] == 'I':  # Scan until it no longer starts with I
                    if guessed[idx] != correct[idx]:
                        correctlyFound = False

                    idx += 1

                if idx < len(guessed):
                    if correct[idx][0] == 'I':  # The chunk in correct was longer
                        correctlyFound = False

                if correctlyFound:
                    correctCount += 1
            else:
                idx += 1
        else:
            idx += 1

    precision = 0
    if count > 0:
        precision = float(correctCount) / count

    return precision

def calculateMatrix(prediction, observation, numberOfClasses):
    comparison = prediction == observation
    acc_ppv = 0
    acc_fdr = 0
    acc_for = 0
    acc_npv = 0
    acc_tpr = 0
    acc_fpr = 0
    acc_tp = 0
    acc_fp = 0
    acc_tn = 0
    acc_fn = 0

    for i in xrange(numberOfClasses):
        positives = comparison[prediction == i]
        negatives = comparison[prediction != i]
        true_positives = np.sum(positives)
        false_positives = np.sum(positives == False)
        true_negatives = np.sum(negatives)
        false_negatives = np.sum(negatives == False)
        if(len(positives) == 0):
            ppv = 1
            fdr = 0
        else:
            ppv = true_positives / float(len(positives))
            fdr = false_positives / float(len(positives))
        if(len(negatives) == 0):
            faor = 0
            npv = 1
        else:
            faor = true_negatives / float(len(negatives))
            npv = false_negatives / float(len(negatives))
        tpr = true_positives / float(true_positives + false_negatives)
        fpr = false_positives / float(false_positives + true_negatives)

        acc_ppv += ppv
        acc_fdr += fdr
        acc_for += faor
        acc_npv += npv
        acc_tpr += tpr
        acc_fpr += fpr

        acc_tp += true_positives
        acc_fp += false_positives
        acc_tn += true_negatives
        acc_fn += false_negatives

    acc_ppv /= float(numberOfClasses)
    acc_fdr /= float(numberOfClasses)
    acc_for /= float(numberOfClasses)
    acc_npv /= float(numberOfClasses)
    acc_tpr /= float(numberOfClasses)
    acc_fpr /= float(numberOfClasses)

    accuracy = (acc_tp + acc_tn) / float(numberOfClasses) / float(len(prediction))
    micro_precision = acc_tp / float(acc_tp + acc_fp)
    macro_precision = acc_ppv
    micro_recall = acc_tp / float(acc_tp + acc_fn)
    macro_recall = acc_tpr
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall)
    macro_f1 = 2 * macro_precision * macro_recall / (macro_precision + macro_recall)

    print 'micro_precision', micro_precision
    print 'micro_recall', micro_recall
    print 'macro_precision', macro_precision
    print 'macro_recall', macro_recall
    print 'micro_f1', micro_f1
    print 'macro_f1', macro_f1
    print 'accuracy', accuracy

    return micro_precision, micro_recall, macro_precision, macro_recall, micro_f1, macro_f1, accuracy