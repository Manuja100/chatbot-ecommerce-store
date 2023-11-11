#import necessary libs
import nltk 
import json 
import pickle
import numpy as np
import random

from keras.models import Sequential
from keras.layers import Dense, Dropout


#create lists for reading the intents file
words = []
classes = []
documents = []
ignore_words = ['?', '!']
data_file = open('intents.json', encoding='utf-8').read()
intents = json.load(data_file)
lemmatier = WordNetLemmatizer()


for intent in intents['intents']:
    for pattern in intent['patterns']:
        #tokenize the pattern and add to the words list
        w = nltk.word_tokenize(pattern)
        words.extend(w)
        
        #add a tuple where w is a list of words of the pattern and the intent['tag'] is the label associated with the intent
        documents.append((w, intent['tag']))

        #used to store all unique tags
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

#without the ignore words we lemmatize the words
words = [lemmatier.lemmatize(w.lower()) for w in words if w not in ignore_words]

#sort the two arrays so the input and output layers of the neural network is consistent
words = sorted(list(set(words)))
classes = sorted(list(set(classes)))

#store for later use in the program
pickle.dump(words,open('words.pkl','wb'))
pickle.dump(classes,open('classes.pkl','wb'))

# initializing training data
training = []
output_empty = [0] * len(classes)


## iterating through documents array to create the training dataset
for doc in documents:

    bag = []

    pattern_words = doc[0]  #Assigning pattern in each of the documents elements
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words] #lemmatizing the pattern words

    #creating the input layer based on the index at which words in corpus appear in pattern_words
    for w in words:
        bag.append(1) if w in pattern_words else bag.append(0)
   
    #creating the output layer based on the tag 
    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])

#shuffling the training dataset to get a better accuracy
random.shuffle(training)

training = np.array(training, dtype = 'object')


# create train and test lists. X - patterns, Y - intents
train_x = list(training[:,0])
train_y = list(training[:,1])

# Building the optimized model
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5)) 
model.add(Dense(len(train_y[0]), activation='softmax'))


model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

#fitting and saving the model
hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
model.save('chatbot_model.h5', hist)







