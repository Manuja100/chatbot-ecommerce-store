from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS
import functions
from pprint import PrettyPrinter
import nltk
from nltk.corpus import stopwords
app = Flask(__name__)
CORS(app, support_credentials=True)
printer = PrettyPrinter()


@app.route('/', methods=["GET", "POST"])
def index():
    return ""

#route which enables the chatbot 
#user uses the following route to communicate from the frontend to the backend
@app.route('/chatbot', methods=["POST"],strict_slashes = False)
def chatbotResponse():

    if request.method == 'POST':
        the_question = request.json['question']

        response = processor.chatbot_response(the_question)

    return jsonify({"response": response })

@app.route('/chats')
def home():
    client = MongoClient("mongodb+srv://it21323966:it21323966@chatbot.nwchqbe.mongodb.net/")
    db = client["ecommerce"]
    mycol = db["products"]

#     mylist = [
#   { "product": "T-shirt", "brand": ["Levis's", "DeeDat", "Emerald", "Envoy"], "price": "5000"},
#   { "product": "shorts", "brand": ["Levis's", "DeeDat", "Emerald", "Envoy"],"price": "3000"},
#   { "product": "Trousers","brand": ["Levis's", "DeeDat", "Emerald", "Envoy"], "price": "2000"},
#   { "product": "socks", "brand": ["Levis's", "DeeDat", "Emerald", "Envoy"],"price": "3000"},
# ]
#     x = mycol.insert_many(mylist)

    query = "What are the Trouser brands".split(" ")
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

    printer.pprint(list(result)[0]['product'])
    
    return ""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)
