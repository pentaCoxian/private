import json
from pymongo import MongoClient
import bson
import pymongo
import certifi
import urllib.parse

def application(environ, start_response):
    originSite = 'icu-syllabus.com'
    headers = [('Content-Type', 'application/json; charset=utf-8'),('Access-Control-Allow-Origin',originSite)]
    start_response('200 OK', headers)

    dbname = get_database()
    cols = dbname["courseOfferings"]
    inputwords = str(urllib.parse.unquote(environ['QUERY_STRING'])).split("+")
    
    if inputwords[0] == '':
        inputwords[0] = ' '

    pipeline = [
  {
    '$search': {
      'index': 'courseSearchIndex',
      'compound':{
          'must': [ {
                'text': {
                    'query': inputwords, 
                    'path': { 'wildcard': '*' }
                        }
                    }
                ]
      }
    }},
    {'$addFields':{'score':{'$meta':'searchScore'}}},
    {'$match':{'score': {'$gt': 2}}}
]

    
    mydoc = cols.aggregate(pipeline)
    resList = []
    for x in mydoc:
        resList.append(x)
    res = json.dumps(resList,ensure_ascii=False).encode('utf-8')
    # res = json.dumps(environ).encode('utf-8') #print environ
    return [res]


def get_database():
    
    from pymongo import MongoClient
    import pymongo
    import certifi
    ca = certifi.where()

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://python:lolpython556@pythondev.etdrtaj.mongodb.net/pythondev"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING, tlsCAFile=ca)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['icu']
