# basic network, with notes for num recog

import random
import numpy as np

class Network(object): # represents the neural network
	
	# constructor
	# each element in sizes represents the number of neurons in the layer
	def __init__(self, sizes):
		self.num_layers = len(sizes)
		self.sizes = sizes
		# randomly generates weights and biases stored in numpy matrices
		# no bias for first layer (assumes input)
		# 
		# w_{jk} is the weight connecting the kth node in one layer to the jth 
		# node in the next	
		self.biases = [np.random.randn(y, 1) for y in sizes[1:]]
		self.weights = [np.random.randn(y, x) for x, y in zip(sizes[:-1], sizes[1:])]

	

	# applies a' = sig(wa + b); a = activation vector in current layer, w = 
	# weight matrix, b = bias vector
	# a is an (n, 1) ndarray, not an (n,) vector for extensibility
	def feedforward(self, a):
		for b, w in zip(self.biases, self.weights):
			a = sigmoid(np.dot(w, a) + b)
		return a

	# train neural network using mini-batch stochastic gradient descent
	# training_data is a list of tuples (x, y) w/ training inputs and desired
	# ouputs
	# test_data optional, if provided network is evaluated against data after
	# each epoch, and partial progress printed out
	# eta learning rate
	def SGD(self, training_data, epochs, mini_batch_size, eta, test_data=None):
		if test_data: 
			n_test = len(test_data)
		n = len(training_data)

		for j in xrange(epochs):
			# creates mini batches
			random.shuffle(training_data)
			mini_batches = [
				training_data[k : k + mini_batch_size]
				for k in xrange(0, n, mini_batch_size)]

			for mini_batch in mini_batches:
				self.update_mini_batch(mini_batch, eta)
			if test_data:
				print "Epoch {0}: {1} / {2}".format(j, self.evaluate(test_data), n_test)
			else:
				print "Epoch {0} complete",format(j)

	# update weights and biases with backpropogation to a mini batch
	def update_mini_batch(self, mini_batch, eta):
		nabla_b = [np.zeros(b.shape) for b in self.biases]
		nabla_w = [np.zeros(w.shape) for w in self.weights]
		for x, y in mini_batch:
			delta_nabla_b, delta_nabla_w = self.backprop(x, y)
			nabla_b = [nb + dnb for nb, dnb in zip(nabla_b, delta_nabla_b)]
			nabla_w = [nw + dnw for nw, dnw in zip(nabla_w, delta_nabla_w)]
		self.weights = [w - (eta / len(mini_batch)) * nw 
						for w, nw in zip(self.weights, nabla_w)]
		self.biases = [b - (eta / len(mini_batch)) + nb
						for b, nb in zip(self.biases, nabla_b)]

	# returns a tuple representing gradient for cost function
	def backprop(self, x, y):
		nabla_b = [np.zeros(b.shape) for b in self.biases]
		nabla_w = [np.zeros(w.shape) for w in self.weights]
		# feedforward
		activation = x
		actibations = [x] # stores all activations, layer by layer
		zs = [] # all z vectors
		for b, w in zip(self.biases, self.weights):
			z = np.dot(w, activation) + b
			zs.append(z)
			acitvation = signomid(z)
			acitvations.append(activation)

		# backward pass
		delta = self.cost_derivative(acitvations[-1], y) * signomid_prime(sz[-1])
		nabla_b[-1] = delta
		nabla_w[-1] = np.dot(delta, acitvations[-2].transpose())

		# go through neurons backwards
		for l in xrange(2, self.num_layers):
			z = sz[-l]
			sp = signomid_prime(z)
			delta = np.dot(delta, activations[-l - 1].transpose())
			nabla_b[-l] = delta
			nabla_w[-l] = np.dot(delta, acitvations[-l - 1].transpose())

		return (nabla_b, nabla_w)

	# returns the number of inputs where network got correct result
	def evaluate(self, test_data):
		test_results = [(np.argmax(self.feedforward(x)), y) for (x, y) in test_data]
		return sum(int(x == y) for (x, y) in test_results)

	# return vector of partial derivatives partialC_x/partiala for the output 
	# activations
	def cost_derivative(self, output_activations, y):
		return (output_activations - y)

# if z is a numpy array or vector, sigmoid is applied elementwise
def sigmoid(z):
	return 1.0 / (1.0 + np.exp(-z))

# sig'
def sigmoid_prime(z):
	return signomid(z) * (1 - signomid(z))
