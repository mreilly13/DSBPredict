from calendar import c
import os
import numpy as nnp
# import cupy as np
import tensorflow as tf
from numpy import loadtxt
from tensorflow import keras
from tensorflow.keras import utils
from tensorflow.keras.layers import BatchNormalization, Dense, Dropout
from tensorflow.keras.models import Sequential
from NNModel.Util.helper import LossAndErrorPrintingCallback, _compare_results, fix_vectors

def load_data():
    """ Load preparsed data """

    # data = np.genfromtxt("tmp/data.csv", delimiter=",")

    cwd = os.getcwd()
    rich_ss_fp = "/Data/RichSS/"
    rich_ss = os.listdir(cwd + rich_ss_fp)
    rich_ss.sort()
    
    # data = np.zeros((1, 9))
    data = nnp.zeros((1, 9))

    for i in rich_ss:
        # pdb_data = np.genfromtxt(cwd + rich_ss_fp + i, delimiter=",")
        # if pdb_data.shape == (9,):
            # pdb_data = np.array([pdb_data])
        # data = np.append(data,pdb_data,axis=0)
        # pdb_data = np.genfromtxt(cwd + rich_ss_fp + i, delimiter=",")
        pdb_data = nnp.genfromtxt(cwd + rich_ss_fp + i, delimiter=",")
        if pdb_data.shape == (9,):
            pdb_data = nnp.array([pdb_data])
        data = nnp.append(data,pdb_data,axis=0)
    
    data = data[1:]

    # features = np.copy(data[:, 0:4])
    features = nnp.copy(data[:, 0:4])
    
    # preprocessing
    features[:, 0] = features[:, 0] / 20.0
    # features[:, 1] = features[:, 1] / np.pi
    # features[:, 2] = features[:, 2] / np.pi
    # features[:, 3] = features[:, 3] / np.pi
    features[:, 1] = features[:, 1] / nnp.pi
    features[:, 2] = features[:, 2] / nnp.pi
    features[:, 3] = features[:, 3] / nnp.pi
    
    # labels = np.copy(data[:, 4])
    labels = nnp.copy(data[:, 4])
    # print(features.shape, labels.shape)
    # return [features.get(), labels.get()]
    return [features, labels]

# meant to be used when testing a loaded model.
def load_single_data(_data):
    """ load individual file data """

    data = _data
    features = nnp.copy(data[:, 0:4]).astype(nnp.float32)
    
    # preprocessing
    features[:, 0] = features[:, 0] / 20.0
    features[:, 1] = features[:, 1] / nnp.pi
    features[:, 2] = features[:, 2] / nnp.pi
    features[:, 3] = features[:, 3] / nnp.pi

    labels = nnp.copy(data[:, 4:])

    return [features, labels]

def load_ss_data():
    data = load_data()
    features = data[0]
    labels = data[1]

    ss_features = []
    non_ss_features = []

    for i in range(len(features)):
        if labels[i] == 1:
            ss_features.append(features[i])
        else:
            non_ss_features.append(features[i])
    ss_features = nnp.array(ss_features)
    ss_labels = nnp.ones((len(ss_features)))
    non_ss_features = nnp.array(non_ss_features)
    non_ss_labels = nnp.zeros((len(non_ss_features)))

    noise = len(non_ss_features) * .01
    noise = int(noise)

    noise_features = non_ss_features[:noise, :]
    noise_labels = non_ss_labels[:noise]
    # print(ss_features.shape, ss_labels.shape)
    # print(noise_features.shape, noise_labels.shape)

    features = nnp.append(ss_features, noise_features, axis= 0)
    labels = nnp.append(ss_labels, noise_labels, axis= 0)
    # print(features.shape, labels.shape)
    
    # print(ss_labels.shape, ss_features.shape)
    return [features, labels]

def _test_load_data():
    """ use this only for internal testing """

    # data = np.genfromtxt("tmp/data.csv", delimiter=",")
    # features = np.copy(data[:, 0:4])
    data = nnp.genfromtxt(os.getcwd() + "/NNModel/Tmp/data.csv", delimiter=",")
    features = nnp.copy(data[:, 0:4])
    
    # preprocessing
    features[:, 0] = features[:, 0] / 20.0
    # features[:, 1] = features[:, 1] / np.pi
    # features[:, 2] = features[:, 2] / np.pi
    # features[:, 3] = features[:, 3] / np.pi
    features[:, 1] = features[:, 1] / nnp.pi
    features[:, 2] = features[:, 2] / nnp.pi
    features[:, 3] = features[:, 3] / nnp.pi

    # labels = np.copy(data[:, 4])
    labels = nnp.copy(data[:, 4:])

    # print(features.shape, labels.shape)

    # return [features.get(), labels.get()]
    return [features, labels]

"""
TODO:
    Will try experimenting with 
    - AdaMax Optimizer
    - AdaGrad Optimizer
"""
def neural_network(data, batchNormalize=True, learning_rate=0.00001, batch_training=False, activation_function='ReLU'):
    """ Neural Network Model """

    # load the data in.
    x_train = data[0]
    x_validate = data[1]
    x_test = data[2]

    y_train = data[3]
    y_validate = data[4]
    y_test = data[5]

    # Hyperparameters:
    num_epochs = 20
    # batch_size = 100
    batch_size = 75
    
    if batch_training:
        num_epochs = 1
        batch_size = 1

    eta = learning_rate
    decay_factor = 0.95
    # size_hidden = 500 # nodes per layer
    size_hidden = 300

    # static parameters
    size_input = 4 # number of features
    size_output =  2 # number of labels
    Input_shape = (size_input,)

    # Neural Network Model
    _model = []
    _model.append(keras.Input(shape=Input_shape, name='input_layer'))
    _model.append(Dense(size_hidden, activation=activation_function, name='hidden_layer01'))
    
    if batchNormalize:
        _model.append(BatchNormalization())
    
    _model.append(Dense(size_hidden, activation=activation_function, name='hidden_layer02'))
    _model.append(Dropout(.05))
    _model.append(Dense(size_hidden, activation=activation_function, name='hidden_layer03'))
    
    if batchNormalize:
        _model.append(BatchNormalization())
    
    _model.append(Dense(size_hidden, activation=activation_function, name='hidden_layer04'))
    _model.append(Dropout(.05))
    _model.append(Dense(size_hidden, activation=activation_function, name='hidden_layer05'))
    
    if batchNormalize:
        _model.append(BatchNormalization())

    _model.append(Dense(size_hidden, activation=activation_function, name='hidden_layer06'))
    _model.append(Dense(size_hidden, activation=activation_function, name='hidden_layer07'))
    _model.append(Dense(size_output, activation='softmax', name='output_layer'))

    model = Sequential(_model)

    # Model information
    model.summary()

    # initializing label in vector form [1, 0, ...], [0, 1, ...], ...
    y_train_vectors = keras.utils.to_categorical(y_train)
    y_test_vectors = keras.utils.to_categorical(y_test)
    y_validate_vectors = keras.utils.to_categorical(y_validate)

    y_train_vectors = fix_vectors(y_train_vectors)
    y_test_vectors = fix_vectors(y_test_vectors)
    y_validate_vectors = fix_vectors(y_validate_vectors)

    # setting up optimizer and scheduler
    learning_rate_schedule = keras.optimizers.schedules.ExponentialDecay(initial_learning_rate=eta, decay_steps=x_train.shape[0], decay_rate=decay_factor)

    optimizer = keras.optimizers.Adam(learning_rate=learning_rate_schedule)
                #keras.optimizers.Adamax(learning_rate=learning_rate_schedule)
                #keras.optimizers.Adagrad(learning_rate=learning_rate_schedule) 
                #keras.optimizers.SGD(learning_rate=learning_rate_schedule)
    
    loss_function = keras.losses.categorical_crossentropy

    # setting up model.
    model.compile(loss=loss_function, optimizer=optimizer, metrics='accuracy')

    if batch_training: # we are training with a epoch of 1 and batch_size of 1 to obtain the learning curve.
        _batch_learning_curve_info = LossAndErrorPrintingCallback()
        
        # history.history['accuracy']['val_accuracy']['loss']['val_loss']
        _history = model.fit(x_train, y_train_vectors, batch_size=batch_size, epochs=num_epochs, validation_data=(x_validate, y_validate_vectors), verbose=2, callbacks=[_batch_learning_curve_info])
    else:
        _history = model.fit(x_train, y_train_vectors, batch_size=batch_size, epochs=num_epochs, validation_data=(x_validate, y_validate_vectors), verbose=2)

    # [loss, accuracy]
    results = model.evaluate(x_test, y_test_vectors, batch_size)

    # prediction
    predictions = model.predict(x_test)

    # Return this
    _prediction_info = _compare_results(predictions, y_test_vectors)
    
    correct = _prediction_info[2]
    wrong = _prediction_info[3]
    total = correct + wrong
    print("Total: " + str(total) + ", Correct: " + str(correct) + ", Incorrect: " + str(wrong))

    # fit, evaluation, prediction
    if batch_training:
        return [_history, results, _prediction_info, _batch_learning_curve_info.returnTraining(), _batch_learning_curve_info.returnTesting(), model]
    
    return [_history, results, _prediction_info, model]

def regression_neural_network(data, epoch=15, learning_rate=0.00001, layers=5, nodes=250):
    if layers > 100:
        print("\n\n\nWarning: Exceeding 100 layers is not recommended.\n\n\n")
    
    if nodes > 1000:
        print("\n\n\nWarning: Exceeding 1000 nodes per layer is not recommended.\n\n\n")

    if learning_rate > 0.01:
        print("\n\n\nWarning: Large learning rate may have poor training results.\n\n\n")
    
    if epoch > 50:
        print("\n\n\nWarning: large epoch size may result in long training time and overfitting.\n\n\n")

    x_train = data[0]
    x_validate = data[1]
    x_test = data[2]

    y_train = data[3]
    y_validate = data[4]
    y_test = data[5]

    num_epochs = epoch
    batch_size = 25
    
    eta = learning_rate
    decay_factor = 0.95
    size_hidden = nodes

    size_input = 4 # number of features
    size_output =  2 # number of labels
    Input_shape = (size_input,)

    _model = []
    _model.append(keras.Input(shape=Input_shape, name='input_layer'))
    _model.append(Dense(size_hidden, activation='ReLU', name='hidden_layer1'))
    _model.append(BatchNormalization())
    for i in range(2, layers+2):
        _model.append(Dense(size_hidden, activation='ReLU', name=('hidden_layer' + str(i))))

    _model.append(Dense(size_output, activation='softmax', name='output_layer'))

    model = Sequential(_model)

    # Model information
    model.summary()

    y_train_vectors = keras.utils.to_categorical(y_train)
    y_test_vectors = keras.utils.to_categorical(y_test)
    y_validate_vectors = keras.utils.to_categorical(y_validate)

    y_train_vectors = fix_vectors(y_train_vectors)
    y_test_vectors = fix_vectors(y_test_vectors)
    y_validate_vectors = fix_vectors(y_validate_vectors)

    learning_rate_schedule = keras.optimizers.schedules.ExponentialDecay(initial_learning_rate=eta, decay_steps=x_train.shape[0], decay_rate=decay_factor)
    optimizer = keras.optimizers.SGD(learning_rate=learning_rate_schedule)
                # keras.optimizers.Adamax(learning_rate=learning_rate_schedule)
                # keras.optimizers.Adam(learning_rate=learning_rate_schedule)
    loss_function = keras.losses.categorical_crossentropy

    model.compile(loss=loss_function, optimizer=optimizer, metrics='accuracy')

    _history = model.fit(x_train, y_train_vectors, batch_size=batch_size, epochs=num_epochs, validation_data=(x_validate, y_validate_vectors), verbose=2)

    results = model.evaluate(x_test, y_test_vectors, batch_size)

    predictions = model.predict(x_test)
    print(predictions)

    return model

def run_LRModel(model, data):
    features = data[0]
    labels = data[1]
    predictions = model.predict(features)

    print("known bonds")
    for i in range(len(labels)):
        if labels[i][0] == 1:
            print(labels[i], predictions[i])
    
    print("possible bonds")
    for i in range(len(labels)):
        if labels[i][1] == 1:
            print(labels[i], predictions[i])

    print(predictions)
    print(predictions.shape)
    # predictions = predictions.reshape(len(predictions), 1)
    # output = np.append(labels, predictions, axis = 1)
    output = nnp.append(labels, predictions, axis = 1)
    # print(output)
    return output

def run_NNModel_Legacy(model, data):
    features = data[0]
    labels = data[1]
    # print(labels)
    y_vectors = utils.to_categorical(labels)
    y_vectors = fix_vectors(y_vectors)
    predictions = model.predict(features)
    _prediction_info = _compare_results(predictions, y_vectors)
    y_predicted = _prediction_info[0]

    h, w = y_predicted.shape
    # print(y_predicted.shape, y_vectors.shape)
    # special_interest = np.zeros((h, w - 1))
    special_interest = nnp.zeros((h, w - 1))
    for i in range(len(y_vectors)):
        if y_predicted[i][0] != y_vectors[i][0] and y_predicted[i][1] != y_vectors[i][1]:
            if y_vectors[i][0] == 1 and y_vectors[i][1] == 0 and y_predicted[i][0] == 0 and y_predicted[i][1] == 1:
                special_interest[i] = 1

    labels = labels.reshape(len(labels), 1)
    # newLabels = np.append(labels, special_interest, axis = 1)
    newLabels = nnp.append(labels, special_interest, axis = 1)
    # print(newLabels)
    return [features, newLabels]

def run_NNModel(model, data):
    features = data[0]
    labels_raw = data[1]
    labels = labels_raw[:, 0].astype(nnp.float32)
    # print(labels)
    y_vectors = utils.to_categorical(labels)
    y_vectors = fix_vectors(y_vectors)
    predictions = model.predict(features)
    _prediction_info = _compare_results(predictions, y_vectors)
    y_predicted = _prediction_info[4]
    y_processed_predicted = _prediction_info[0]
    return nnp.append(y_predicted, labels_raw, axis = 1)

    # h, w = y_predicted.shape
    # print(y_predicted.shape, y_vectors.shape)
    # special_interest = np.zeros((h, w - 1))
    # for i in range(len(y_vectors)):
    #     if y_predicted[i][0] != y_vectors[i][0] and y_predicted[i][1] != y_vectors[i][1]:
    #         if y_vectors[i][0] == 1 and y_vectors[i][1] == 0 and y_predicted[i][0] == 0 and y_predicted[i][1] == 1:
    #             special_interest[i] = 1

    # labels = labels.reshape(len(labels), 1)
    # newLabels = np.append(labels, special_interest, axis = 1)
    # print(newLabels)
    # return [features, newLabels]

def save_model(model, fileName):
    cwd = os.getcwd()
    sm_path = "/NNModel/SavedModels/"
    os.makedirs(os.path.dirname(cwd + sm_path), exist_ok=True)
    model.save(cwd + sm_path + fileName)

def load_model(fileName):
    cwd = os.getcwd()
    sm_path = "/NNModel/SavedModels/"
    model = keras.models.load_model(cwd + sm_path + fileName)
    model.summary()
    return model