from Classification import *
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def mlp(xTrain, xTest, yTrain, yTest, iNeurons: int = 2, oNeurons: int = 1):
	temp = []
	for i in range(xTrain.shape[1]):
		temp.append([0.5]*iNeurons)
	w1 = np.array([]+temp)
	w2 = np.array([0.5]*iNeurons)
	b1 = np.array([0.5]*iNeurons)
	b2 = np.array([0.5]*oNeurons)
	f = lambda x: 1.0/(1.0 + np.exp(-x))
	for i in range(len(xTrain)):
		h1 = f(np.dot(w1.T, xTrain[i]) + b1)  # dot product of w1 with x, then adding b1
		# Assuming the output layer is directly connected to the first hidden layer
		yhat = f(np.dot(w2, h1) + b2)  # dot product of w2 with h1, then adding b2
		# Computing the loss
		loss = np.square(y - yhat)  # Squared error loss
		print(yhat, loss)
	

def contains_not(text):
    return 1 if 'not' in text.split() else 0

def contains_security(text):
    return 1 if 'security' in text.split() else 0
    
if __name__ == "__main__":
	dataset = pd.read_csv('emails.csv', encoding='ISO-8859-1')
	feature_functions = [contains_not, contains_security]
	X_featureless, feature_names = bag_of_wordsify(dataset=dataset,feature_functions=[], max_token_features=50)
	X, feature_names = bag_of_wordsify(dataset=dataset,feature_functions=feature_functions, max_token_features=50)

	y = dataset['spam']

	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

	print(X_train.shape, X_test.shape, y_train.shape, y_test.shape)
	mlp(X_train, X_test, y_train, y_test)

