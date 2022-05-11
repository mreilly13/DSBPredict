from calendar import c
import os
import numpy as np
import tensorflow as tf
from numpy import loadtxt
from tensorflow import keras
from tensorflow.keras import utils
from tensorflow.keras.layers import BatchNormalization, Dense, Dropout
from tensorflow.keras.models import Sequential
from util.helper import LossAndErrorPrintingCallback, _compare_results, fix_vectors

#from sqlite3 import adapt


def load_data():
    """ Load preparsed data """

    """
    TODO:
        Remove hardcoded data path and replace with parsed
        pdb file getter.
    """ 
    #data = np.genfromtxt("tmp/data.csv", delimiter=",")

    csv_type = [
    ('dist', np.float64), 
    ('omega', np.float64), 
    ('theta', np.float64), 
    ('phi', np.float64),
    ('ssbond', np.int32),
    ('chain1', (np.str_,1)),
    ('res1', np.int32),
    ('chain2', (np.str_,1)),
    ('res2', np.int32)
    ]
    cwd = os.getcwd()
    cwd = cwd[:len(cwd) - 8]
    rich_ss_fp = "/Data/Rich_SS/"
    rich_ss = os.listdir(cwd + rich_ss_fp)
    rich_ss.sort()
    
    data = np.zeros((1, 9))

    for i in rich_ss:
        pdb_data = np.genfromtxt(cwd + rich_ss_fp + i, delimiter=",")
        #pdb_data = np.loadtxt(cwd + rich_ss_fp + i, dtype=csv_type, delimiter=',')
        #print(i, str(pdb_data.shape) + "\n")
        if pdb_data.shape == (9,):
            pdb_data = np.array([pdb_data])
        data = np.append(data,pdb_data,axis=0)
    


    

    features = np.copy(data[:, 0:4])
    
    # preprocessing
    features[:, 0] = features[:, 0] / 20.0
    features[:, 1] = features[:, 1] / np.pi
    

    labels = np.copy(data[:, 4])

    print(features.shape, labels.shape)

    return [features, labels]


"""
TODO:
    Will try experimenting with 
    - AdaMax Optimizer
    - AdaGrad Optimizer
"""
def neural_network(data, batchNormalize=True, learning_rate=0.0001, batch_training=False, activation_function='ReLU'):
    """ Neural Network Model """

    # load the data in.
    x_train = data[0]
    x_validate = data[1]
    x_test = data[2]

    y_train = data[3]
    y_validate = data[4]
    y_test = data[5]


    # Hyperparameters:
    num_epochs = 25
    batch_size = 100
    if batch_training:
        num_epochs = 1
        batch_size = 1

    eta = learning_rate
    decay_factor = 0.95
    size_hidden = 500 # nodes per layer

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
    #_model.append(Dropout(.2))
    _model.append(Dense(size_hidden, activation=activation_function, name='hidden_layer03'))
    _model.append(Dense(size_hidden, activation=activation_function, name='hidden_layer04'))
    _model.append(Dense(size_hidden, activation=activation_function, name='hidden_layer05'))
    _model.append(Dense(size_output, activation='softmax', name='output_layer'))

    model = Sequential(_model)


    # Model information
    model.summary()


    # initializing label in vector form [1, 0, ...], [0, 1, ...], ...
    y_train_vectors = utils.to_categorical(y_train)
    y_test_vectors = utils.to_categorical(y_test)
    y_validate_vectors = utils.to_categorical(y_validate)

    y_train_vectors = fix_vectors(y_train_vectors)
    y_test_vectors = fix_vectors(y_test_vectors)
    y_validate_vectors = fix_vectors(y_validate_vectors)


    # setting up optimizer and scheduler
    learning_rate_schedule = keras.optimizers.schedules.ExponentialDecay(initial_learning_rate=eta, decay_steps=x_train.shape[0], decay_rate=decay_factor)

    optimizer = keras.optimizers.Adam(learning_rate=learning_rate_schedule)
                #keras.optimizers.Adamax(learning_rate=learning_rate_schedule)
                #keras.optimizers.Adamgrad(learning_rate=learning_rate_schedule) 
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


def save_model(model, fileName):
    path = "saved_models/"
    model.save(path + fileName)