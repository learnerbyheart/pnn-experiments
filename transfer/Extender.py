from keras.utils import np_utils
from keras.layers import Input

def extendInputs(additional_models_for_input, model_train_input, model_dev_input, model_test_input):
    model_train_input_ext = []
    model_dev_input_ext = []
    model_test_input_ext = []
    model_train_input_ext.extend(model_train_input)
    model_dev_input_ext.extend(model_dev_input)
    model_test_input_ext.extend(model_test_input)
    for model in additional_models_for_input:
        num_layers = len(model.layers)
        output_dim = model.layers[num_layers - 1].output_dim
        additional_train = model.predict(model_train_input, verbose=0).argmax(axis=-1)
        additional_train = np_utils.to_categorical(additional_train, output_dim)
        additional_dev = model.predict(model_dev_input, verbose=0).argmax(axis=-1)
        additional_dev = np_utils.to_categorical(additional_dev, output_dim)
        additional_test = model.predict(model_test_input, verbose=0).argmax(axis=-1)
        additional_test = np_utils.to_categorical(additional_test, output_dim)

        model_train_input_ext.extend([additional_train])
        model_dev_input_ext.extend([additional_dev])
        model_test_input_ext.extend([additional_test])
    return model_train_input_ext, model_dev_input_ext, model_test_input_ext

def buildInputLayerWithAdditionalModels(additional_models):
    additional_input_layer = []
    i = 1
    for model in additional_models:
        layer_name = "additional_input_layer" + str(i)
        num_layers = len(model.layers)
        output_dim = model.layers[num_layers -1].output_dim
        additional_input_layer.append(Input(shape=(output_dim,), dtype='float32', name=layer_name))
    return additional_input_layer