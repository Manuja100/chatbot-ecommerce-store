import nltk
import json
import random
import pickle
import numpy as np
import re
import nltk
from pymongo import MongoClient
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


model = load_model('chatbot_model.h5')
intents = json.loads(open('../intents.json', encoding='utf-8').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))
lemmatizer = WordNetLemmatizer()

#connect moongodb cluster
client = MongoClient("mongodb+srv://it21323966:it21323966@chatbot.nwchqbe.mongodb.net/")
db = client["ecommerce"]


def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1

    return(np.array(bag))


def predict_class(sentence, model):
    # filter out predictions below a threshold

    p = bow(sentence, words)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []

    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(msg,ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']

    mycol = db["products"]

    result = "return I'm sorry, I don't understand that."

    ## The following for loop returns responses to user based on whether they
    ## are normal intents or require database retrievel
    for i in list_of_intents:
        if(i['tag']== tag):

            #Display products funtion
            if tag == 'products':

                result = "We sell "
                results = mycol.find({})
                
                for doc in results:
                    result += doc['product'] + " "
                
                return result
            
            #Tracking order function
            elif tag == "track":
                order_id = extract_order_id(msg)

                if order_id:
                    order_status, result = getOrderStatus(order_id)
                else:
                    result = "Please provide me with order details"

                return result
            
            #Showing brands function
            elif tag == "brands":
                item, brands = extract_brand(msg)

                result = item + ": "

                for brand in brands:
                    result += brand + " "
                
                return result
            
            #showing prices function
            elif tag == "prices":

                result = "Our prices"
                results = mycol.find({})
                
                for doc in results:
                    result += doc['product'] + ": Rs" + doc['price'] + ", "
                
                return result

            ##Normal intent case
            else:
                result = random.choice(i['responses'])
                break
        
        
            
    return result

#Main function which is called from the app.py to predict output
def chatbot_response(msg):
    ints = predict_class(msg, model)
    res = getResponse(msg, ints, intents)
    return res

#function to get order status of user from database
def getOrderStatus(order_id):
    
    collection = db["orders"]
    order = collection.find_one({"order_id": int(order_id)})
   
    if order:
        order_status = order.get("status", "Status not available")
        response = f"Order Status is: {order_status}\nPlease contact us for further information"
        return(order_status, response)
    else:
        print("Order not found.")

#function to get extract order id from user query
def extract_order_id(user_input):
    order_id = None
    pattern = r"(\d+)"
    match = re.search(pattern, user_input)
    if match:
        order_id = match.group(1)
    return order_id

#function to extract deliver brands of products to user
def extract_brand(user_input):
    mycol = db["products"]

    query = user_input.split(" ")
    stop_words = stopwords.words('english')
    new_query = [word for word in query if word not in stop_words ]
    search_query = ""
    
    for query in new_query:
        search_query += query + " "
    
    result = mycol.aggregate([
        {"$search":{
            "index":"product_search",
            "text":{
                "query":search_query,
                "path": "product",
                "fuzzy": {}
            }
        }}
    ])

    result_list = list(result)
    
    brand = result_list[0]['brand']
    product = result_list[0]['product']
    return product,brand
    


    

