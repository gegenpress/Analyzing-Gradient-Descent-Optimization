'''
This file implements a multi layer neural network for a multiclass classifier
'''
import numpy as np
from load_mnist import mnist
from pprint import pprint


import matplotlib.pyplot as plt
import pdb
import sys, ast
import os


def relu(Z):
    '''
    computes relu activation of Z
    Inputs:
        Z is a numpy.ndarray (n, m)
    Returns:
        A is activation. numpy.ndarray (n, m)
        cache is a dictionary with {"Z", Z}
    '''
    A = np.maximum(0, Z)
    cache = {}
    cache["Z"] = Z
    return A, cache


def relu_der(dA, cache):
    '''
    computes derivative of relu activation
    Inputs:
        dA is the derivative from subsequent layer. numpy.ndarray (n, m)
        cache is a dictionary with {"Z", Z}, where Z was the input
        to the activation layer during forward propagation
    Returns:
        dZ is the derivative. numpy.ndarray (n,m)
    '''
    dZ = np.array(dA, copy=True)
    Z = cache["Z"]
    dZ[Z < 0] = 0
    return dZ


def linear(Z):
    '''
    computes linear activation of Z
    This function is implemented for completeness
    Inputs:
        Z is a numpy.ndarray (n, m)
    Returns:
        A is activation. numpy.ndarray (n, m)
        cache is a dictionary with {"Z", Z}
    '''
    A = Z
    cache = {}
    cache["Z"] = Z
    return A, cache


def linear_der(dA, cache):
    '''
    computes derivative of linear activation
    This function is implemented for completeness
    Inputs:
        dA is the derivative from subsequent layer. numpy.ndarray (n, m)
        cache is a dictionary with {"Z", Z}, where Z was the input
        to the activation layer during forward propagation
    Returns:
        dZ is the derivative. numpy.ndarray (n,m)
    '''
    dZ = np.array(dA, copy=True)
    return dZ


def softmax_cross_entropy_loss(Z, num_classes, Y=np.array([])):
    '''
    Computes the softmax activation of the inputs Z
    Estimates the cross entropy loss
    Inputs:
        Z - numpy.ndarray (n, m)
        Y - numpy.ndarray (1, m) of labels
            when y=[] loss is set to []

    Returns:
        A - numpy.ndarray (n, m) of softmax activations
        cache -  a dictionary to store the activations later used to estimate derivatives
        loss - cost of prediction
    '''
    ### CODE HERE

    Y_new = Y.astype(int)
    Y_L = Y_new.tolist()

    A = np.exp(Z - np.max(Z)) / np.sum(np.exp(Z - np.max(Z)), axis=0, keepdims=True)

    cache = {}
    cache["A"] = A

    if Y.shape[0] == 0:
        loss = []
    else:
        one_hot_Y = one_hot(Y_L, num_classes)
        Y_sm = one_hot_Y.T
        loss = -np.sum(Y_sm * np.log(A + 1e-9)) / A.shape[1]

    return A, cache, loss


def softmax_cross_entropy_loss_der(Y, num_classes, cache):
    '''
    Computes the derivative of softmax activation and cross entropy loss
    Inputs:
        Y - numpy.ndarray (1, m) of labels
        cache -  a dictionary with cached activations A of size (n,m)
    Returns:
        dZ - numpy.ndarray (n, m) derivative for the previous layer
    '''
    ### CODE HERE
    Y_new = Y.astype(int)
    Y_L = Y_new.tolist()

    one_hot_Y = one_hot(Y_L, num_classes)
    Y_smd = one_hot_Y.T
    A = cache["A"]

    dZ = A - Y_smd
    return dZ


def initialize_multilayer_weights(net_dims):
    '''
    Initializes the weights of the multilayer network
    Inputs:
        net_dims - tuple of network dimensions
    Returns:
        dictionary of parameters
    '''
    np.random.seed(0)
    numLayers = len(net_dims)
    parameters = {}
    for l in range(numLayers - 1):
        parameters["W" + str(l + 1)] = np.random.normal(0, np.sqrt(2.0 / net_dims[l]), (net_dims[l + 1], net_dims[l]))
        parameters["b" + str(l + 1)] = np.random.normal(0, np.sqrt(2.0 / net_dims[l]), (net_dims[l + 1], 1))
    return parameters


def linear_forward(A, W, b):
    '''
    Input A propagates through the layer
    Z = WA + b is the output of this layer.
    Inputs:
        A - numpy.ndarray (n,m) the input to the layer
        W - numpy.ndarray (n_out, n) the weights of the layer
        b - numpy.ndarray (n_out, 1) the bias of the layer
    Returns:
        Z = WA + b, where Z is the numpy.ndarray (n_out, m) dimensions
        cache - a dictionary containing the inputs A
    '''
    ### CODE HERE
    Z = np.dot(W, A) + b

    cache = {}
    cache["A"] = A
    return Z, cache


def layer_forward(A_prev, W, b, activation):
    '''
    Input A_prev propagates through the layer and the activation
    Inputs:
        A_prev - numpy.ndarray (n,m) the input to the layer
        W - numpy.ndarray (n_out, n) the weights of the layer
        b - numpy.ndarray (n_out, 1) the bias of the layer
        activation - is the string that specifies the activation function
    Returns:
        A = g(Z), where Z = WA + b, where Z is the numpy.ndarray (n_out, m) dimensions
        g is the activation function
        cache - a dictionary containing the cache from the linear and the nonlinear propagation
        to be used for derivative
    '''
    Z, lin_cache = linear_forward(A_prev, W, b)
    if activation == "relu":
        A, act_cache = relu(Z)
    elif activation == "linear":
        A, act_cache = linear(Z)

    cache = {}
    cache["lin_cache"] = lin_cache
    cache["act_cache"] = act_cache
    return A, cache


def multi_layer_forward(X, parameters):
    '''
    Forward propgation through the layers of the network
    Inputs:
        X - numpy.ndarray (n,m) with n features and m samples
        parameters - dictionary of network parameters {"W1":[..],"b1":[..],"W2":[..],"b2":[..]...}
    Returns:
        AL - numpy.ndarray (c,m)  - outputs of the last fully connected layer before softmax
            where c is number of categories and m is number of samples in the batch
        caches - a dictionary of associated caches of parameters and network inputs
    '''
    L = len(parameters) // 2
    A = X
    caches = []
    for l in range(1, L):  # since there is no W0 and b0
        A, cache = layer_forward(A, parameters["W" + str(l)], parameters["b" + str(l)], "relu")
        caches.append(cache)

    AL, cache = layer_forward(A, parameters["W" + str(L)], parameters["b" + str(L)], "linear")
    caches.append(cache)
    return AL, caches


def linear_backward(dZ, cache, W, b):
    '''
    Backward prpagation through the linear layer
    Inputs:
        dZ - numpy.ndarray (n,m) derivative dL/dz
        cache - a dictionary containing the inputs A, for the linear layer
            where Z = WA + b,
            Z is (n,m); W is (n,p); A is (p,m); b is (n,1)
        W - numpy.ndarray (n,p)
        b - numpy.ndarray (n, 1)
    Returns:
        dA_prev - numpy.ndarray (p,m) the derivative to the previous layer
        dW - numpy.ndarray (n,p) the gradient of W
        db - numpy.ndarray (n, 1) the gradient of b
    '''
    A = cache["A"]
    # print "A : ",A
    # print "A sum : ",np.sum(A)
    # print "W : ",W
    dA_prev = np.dot(W.T, dZ)
    # print "Da : ",dA_prev
    dW = np.dot(dZ, A.T) / A.shape[1]
    # print "DW : ",dW
    # print "DW sum : ",np.sum(dW)
    db = np.sum(dZ, axis=1, keepdims=True) / A.shape[1]
    # print "Db : ",db

    ## CODE HERE
    return dA_prev, dW, db


def layer_backward(dA, cache, W, b, activation):
    '''
    Backward propagation through the activation and linear layer
    Inputs:
        dA - numpy.ndarray (n,m) the derivative to the previous layer
        cache - dictionary containing the linear_cache and the activation_cache
        activation - activation of the layer
        W - numpy.ndarray (n,p)
        b - numpy.ndarray (n, 1)

    Returns:
        dA_prev - numpy.ndarray (p,m) the derivative to the previous layer
        dW - numpy.ndarray (n,p) the gradient of W
        db - numpy.ndarray (n, 1) the gradient of b
    '''
    lin_cache = cache["lin_cache"]
    act_cache = cache["act_cache"]

    if activation == "sigmoid":
        dZ = sigmoid_der(dA, act_cache)
    elif activation == "tanh":
        dZ = tanh_der(dA, act_cache)
    elif activation == "relu":
        dZ = relu_der(dA, act_cache)
    elif activation == "linear":
        dZ = linear_der(dA, act_cache)
    dA_prev, dW, db = linear_backward(dZ, lin_cache, W, b)
    return dA_prev, dW, db


def multi_layer_backward(dAL, caches, parameters):
    '''
    Back propgation through the layers of the network (except softmax cross entropy)
    softmax_cross_entropy can be handled separately
    Inputs:
        dAL - numpy.ndarray (n,m) derivatives from the softmax_cross_entropy layer
        caches - a dictionary of associated caches of parameters and network inputs
        parameters - dictionary of network parameters {"W1":[..],"b1":[..],"W2":[..],"b2":[..]...}
    Returns:
        gradients - dictionary of gradient of network parameters
            {"dW1":[..],"db1":[..],"dW2":[..],"db2":[..],...}
    '''
    L = len(caches)  # with one hidden layer, L = 2
    gradients = {}
    dA = dAL
    activation = "linear"
    for l in reversed(range(1, L + 1)):
        # print "Layer ",l
        dA, gradients["dW" + str(l)], gradients["db" + str(l)] = \
            layer_backward(dA, caches[l - 1], parameters["W" + str(l)], parameters["b" + str(l)], activation)
        activation = "relu"
    return gradients


def classify(X, parameters):
    '''
    Network prediction for inputs X
    Inputs:
        X - numpy.ndarray (n,m) with n features and m samples
        parameters - dictionary of network parameters
            {"W1":[..],"b1":[..],"W2":[..],"b2":[..],...}
    Returns:
        YPred - numpy.ndarray (1,m) of predictions
    '''
    ### CODE HERE
    # Forward propagate X using multi_layer_forward
    # Get predictions using softmax_cross_entropy_loss
    # Estimate the class labels using predictions
    num_classes = 10
    A, _ = multi_layer_forward(X, parameters)
    A, _, _ = softmax_cross_entropy_loss(A, num_classes)
    YPred = np.argmax(A, axis=0)
    return np.reshape(YPred, (1, YPred.shape[0]))


def initialize_velocity(parameters):


    Length = len(parameters) // 2

    velocity = {}
    svelocity = {}

    for i in range(Length):
        velocity["dW" + str(i + 1)] = np.zeros_like(parameters["W" + str(i + 1)])
        velocity["db" + str(i + 1)] = np.zeros_like(parameters["b" + str(i + 1)])

        svelocity["dW" + str(i + 1)] = np.zeros_like(parameters["W" + str(i + 1)])
        svelocity["db" + str(i + 1)] = np.zeros_like(parameters["b" + str(i + 1)])


    return velocity, svelocity


def update_parameters_velocity(parameters, gradients, epoch, velocity, svelocity, t, beta1=0.9, beta2=0.999, epsilon=1e-8, learning_rate=0.0001, decay_rate=0.01):
    '''
    Updates the network parameters with gradient descent
    Inputs:
        parameters - dictionary of network parameters
            {"W1":[..],"b1":[..],"W2":[..],"b2":[..],...}
        gradients - dictionary of gradient of network parameters
            {"dW1":[..],"db1":[..],"dW2":[..],"db2":[..],...}
        epoch - epoch number
        learning_rate - step size for learning
        decay_rate - rate of decay of step size - not necessary - in case you want to use
    '''
    #pprint(parameters)
    alpha = learning_rate * (1 / (1 + decay_rate * epoch))
    L = len(parameters) // 2
    vel_cor = {}
    svel_cor = {}
    for i in range(L):
        velocity["dW" + str(i + 1)] = beta2 * velocity["dW" + str(i + 1)] + (1 - beta2) * gradients["dW" + str(i + 1)]
        velocity["db" + str(i + 1)] = beta2 * velocity["db" + str(i + 1)] + (1 - beta2) * gradients["db" + str(i + 1)]

        vel_cor["dW" + str(i + 1)] = velocity["dW" + str(i + 1)] / (1 - np.power(beta1, t))
        vel_cor["db" + str(i + 1)] = velocity["db" + str(i + 1)] / (1 - np.power(beta1, t))

        svelocity["dW" + str(i + 1)] = beta2 * svelocity["dW" + str(i + 1)] + (1 - beta2) * np.power(gradients["dW" + str(i + 1)], 2)
        svelocity["db" + str(i + 1)] = beta2 * svelocity["db" + str(i + 1)] + (1 - beta2) * np.power(gradients["db" + str(i + 1)], 2)

        svel_cor["dW" + str(i + 1)] = svelocity["dW" + str(i + 1)] / (1 - np.power(beta2, t))
        svel_cor["db" + str(i + 1)] = svelocity["db" + str(i + 1)] / (1 - np.power(beta2, t))

        parameters["W" + str(i + 1)] = parameters["W" + str(i + 1)] - learning_rate * vel_cor["dW" + str(i + 1)]/ np.sqrt(svel_cor["dW" + str(i + 1)] + epsilon)
        parameters["b" + str(i + 1)] = parameters["b" + str(i + 1)] - learning_rate * vel_cor["db" + str(i + 1)]/ np.sqrt(svel_cor["db" + str(i + 1)] + epsilon)

    return parameters, alpha, velocity, svelocity



def one_hot(Y, num_classes):

    if type(Y) == list:
        Y = np.array(Y)
    Y = Y.flatten()

    Y_one_hot = np.zeros((len(Y), num_classes))
    Y_one_hot[np.arange(len(Y)), (Y)] = 1
    return Y_one_hot


def multi_layer_network(X, Y, validation_data, validation_label, net_dims, num_iterations=500, learning_rate=0.0001, decay_rate=0.01, batch_size=10):
    '''
    Creates the multilayer network and trains the network
    Inputs:
        X - numpy.ndarray (n,m) of training data
        Y - numpy.ndarray (1,m) of training data labels
        net_dims - tuple of layer dimensions
        num_iterations - num of epochs to train
        learning_rate - step size for gradient descent

    Returns:
        costs - list of costs over training
        parameters - dictionary of trained network parameters
    '''
    parameters = initialize_multilayer_weights(net_dims)
    A0 = X
    B0 = validation_data
    alpha = learning_rate
    costs = []
    vcosts = []
    num_classes = 10
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    t = 0
    v, sv = initialize_velocity(parameters)
    X_batch_size = np.split(X, batch_size, axis=1)
    Y_batch_size = np.split(Y, batch_size, axis=1)
    batch_length = len(X_batch_size)
    # Y_one_hot = one_hot(Y,num_classes)
    #Y_one_hot = np.zeros((num_classes, Y.shape[1]))
    #for i in range(Y.shape[1]):
        #Y_one_hot[int(Y[0, i]), i] = 1

    # validation_label_one_hot = one_hot(validation_label,num_classes)
    #validation_label_one_hot = np.zeros((num_classes, validation_label.shape[1]))
    #for i in range(validation_label.shape[1]):
        #validation_label_one_hot[int(validation_label[0, i]), i] = 1

    for ii in range(num_iterations):
        for jj in range(batch_length):
            ### CODE HERE
            # Forward Prop
            ## call to multi_layer_forward to get activations
            ## call to softmax cross entropy loss
            Z, caches = multi_layer_forward(X_batch_size[jj], parameters)
            A, cache_cross, cost = softmax_cross_entropy_loss(Z, num_classes, Y_batch_size[jj])

            # Backward Prop
            dZ = softmax_cross_entropy_loss_der(Y_batch_size[jj], num_classes, cache_cross)
            # print dZ
            # print "dz : ",dZ.shape
            # caches.append(cache_cross)

            gradients = multi_layer_backward(dZ, caches, parameters)
            # print "Grad : ",gradients
            # print gradients
            t = t + 1
            parameters, alpha, velocity, svelocity = update_parameters_velocity(parameters, gradients, ii, v, sv, t, beta1, beta2, epsilon, learning_rate, decay_rate)
            # print parameters
            # if ii ==1:
            #     print "Iteration 2"
            #     print "dz : ",dZ
            #     print "Gradients : ",gradients
            #     print "Parameters : ",parameters
            #     exit(0)
            ## call to softmax cross entropy loss der
            ## call to multi_layer_backward to get gradients
            ## call to update the parameters

        #if ii % 10 == 0:
        costs.append(cost)

        VZ, vcaches = multi_layer_forward(B0, parameters)
        B, vcache_cross, vcost = softmax_cross_entropy_loss(VZ, num_classes, validation_label)

        vcosts.append(vcost)
        if ii % 10 == 0:
            print("Training Cost at iteration %i is: %.05f, learning rate: %.05f" % (ii, cost, alpha))
            print("Validation Cost at iteration %i is: %.05f, learning rate: %.05f" % (ii, vcost, alpha))

    return costs, parameters, vcosts


def main():
    '''
    Trains a multilayer network for MNIST digit classification (all 10 digits)
    To create a network with 1 hidden layer of dimensions 800
    Run the progam as:
        python deepMultiClassNetwork_starter.py "[784,800]"
    The network will have the dimensions [784,800,10]
    784 is the input size of digit images (28pix x 28pix = 784)
    10 is the number of digits

    To create a network with 2 hidden layers of dimensions 800 and 500
    Run the progam as:
        python deepMultiClassNetwork_starter.py "[784,800,500]"
    The network will have the dimensions [784,800,500,10]
    784 is the input size of digit images (28pix x 28pix = 784)
    10 is the number of digits
    '''
    n_input, m = 784, 784
    n_hidden1 = 500
    n_hidden2 = 100
    net_dims = [n_input, n_hidden1, n_hidden2]
    #net_dims = ast.literal_eval(sys.argv[1])
    net_dims.append(10)  # Adding the digits layer with dimensionality = 10
    print("Network dimensions are:" + str(net_dims))

    # getting the subset dataset from Fashion_mnist
    orig_train_data, orig_train_label, test_data, test_label = \
        mnist(noTrSamples=6000, noTsSamples=1000, digit_range=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9], noTrPerClass=600,
              noTsPerClass=100)

    train_data = orig_train_data[:, :500]
    train_label = orig_train_label[:, :500]
    validation_data = orig_train_data[:, 500:600]
    validation_label = orig_train_label[:, 500:600]

    for i in range(600, 6000, 600):
        train_data = np.hstack((train_data, orig_train_data[:, i:i + 500]))
        train_label = np.hstack((train_label, orig_train_label[:, i:i + 500]))
        validation_data = np.hstack((validation_data, orig_train_data[:, i + 500:i + 600]))
        validation_label = np.hstack((validation_label, orig_train_label[:, i + 500:i + 600]))

    learning_rate = 0.01
    decay_rate = 0.01
    num_iterations = 500
    batch_size = 10

    costs, parameters, vcosts = multi_layer_network(train_data, train_label, validation_data, validation_label,
                                                    net_dims, num_iterations=num_iterations, learning_rate=learning_rate,
                                                    decay_rate=decay_rate, batch_size=batch_size)

    # compute the accuracy for training set and testing set
    train_Pred = classify(train_data, parameters)
    test_Pred = classify(test_data, parameters)
    val_Pred = classify(validation_data, parameters)

    trAcc = (1 - np.count_nonzero(train_Pred - train_label) / float(train_Pred.shape[1])) * 100
    teAcc = (1 - np.count_nonzero(test_Pred - test_label) / float(test_Pred.shape[1])) * 100
    valAcc = (1 - np.count_nonzero(val_Pred - validation_label) / float(val_Pred.shape[1])) * 100
    print("Accuracy for training set is {0:0.3f} %".format(trAcc))
    print("Accuracy for testing set is {0:0.3f} %".format(teAcc))
    print("Accuracy for validation set is {0:0.3f} %".format(valAcc))

    X = np.arange(0, 500)
    plt.plot(X, costs, label="Train Cost")
    plt.plot(X, vcosts, label="Validation Cost")
    plt.xlabel("No Of Iterations")
    plt.ylabel("Training Cost / Validation Cost")
    plt.title("Cost vs Number of Iterations with " + str(learning_rate) + " Learning rate")
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()