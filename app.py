# -*- coding: utf-8 -*-
from uvicorn import run
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')
import random
import numpy as np
import json
import pickle
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
from tensorflow.python.keras.models import load_model
from fastapi import FastAPI, HTTPException

lemmatizer=WordNetLemmatizer()

with open('intents.json') as json_file:
    intents = json.load(json_file)

words=pickle.load(open('words.pkl','rb'))
classes=pickle.load(open('classes.pkl','rb'))
model=load_model('chatbotmodel.h5')

app=FastAPI() 
@app.get("/")
async def root():
    return {"message": "Welcome here, I am Medi , how can I help you ?"}

def clean_up_sentence(sentence):
  sentence_words=nltk.word_tokenize(sentence)
  sentence_words=[lemmatizer.lemmatize(word) for word in sentence_words]
  return sentence_words

def bag_of_words(sentence):
  sentence_words=clean_up_sentence(sentence)
  bag=[0]*len(words)
  for w in sentence_words:
    for i,word in enumerate(words):
      if word == w:
        bag[i]=1
  return np.array(bag)


def predict_class(sentence):
    bow=bag_of_words(sentence)
    res=model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD=0.25
    results=[[i,r] for i,r in enumerate(res) if r> ERROR_THRESHOLD]

    results.sort(key=lambda x:x[1],reverse=True)
    return_list=[]
    for r in results:
        return_list.append({'intent': classes[r[0]],'probability':str(r[1])})
    return return_list


def get_response(intents_list,intents_json):
    tag=intents_list[0]['intent']
    list_of_intents=intents_json['intents']
    result=""
    for i in list_of_intents:
        if i['tag']==tag:
            result=random.choice(i['responses'])
            break
    return result

# print("GO! BOT IS RUNNING")
# app = FastAPI()
# @app.get("/")
# def root():
#     return {"message": "Welcome here, I am Medi , how can I help you ?"}

@app.post("/get_reply")
async def get_reply(question):
    if(not(question)):
        raise HTTPException(status_code=400, 
                            detail = "Sorry, I can't understand you dear, please write something valid!")
    ints=predict_class(question)
    res=get_response(ints,intents)
    return {
        "question": question, 
        "reply_": res
        }

# while True:
#   message=input("")
#   ints=predict_class(message)
#   res=get_response(ints,intents)
#   print(res)