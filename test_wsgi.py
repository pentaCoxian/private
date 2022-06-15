import json
from pymongo import MongoClient
import bson
import pymongo
import certifi
import urllib.parse

def application(environ, start_response):
    headers = [('Content-Type', 'application/json; charset=utf-8')]
    start_response('200 OK', headers)

    dbname = get_database()
    
    inputwords = str(urllib.parse.unquote(environ['QUERY_STRING'])).split("+")

    # tune for match
    minMatch = len(inputwords) -1

    
    if inputwords[0] == '':
        inputwords[0] = ' '

    # make Qarry from input
    pipeline = makeQuery(inputwords[0],inputwords[1:])
    print(pipeline)

    # set target and aggregate
    cols = dbname["courseSyllabus"]
    mydoc = cols.aggregate(pipeline)

    # convert tp list
    resList = []
    for x in mydoc:
        resList.append(x)
    

    res = json.dumps(resList,ensure_ascii=False).encode('utf-8')


    return [res]


def get_database():
    
    from pymongo import MongoClient
    import pymongo
    import certifi
    ca = certifi.where()

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb+srv://python:lolpython556@pythondev.etdrtaj.mongodb.net/pythondev"
    client = MongoClient(CONNECTION_STRING, tlsCAFile=ca)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['icu']

def makeFilterList(input):
  resList = []
  for x in input:
    resList.append({'text': {'query': x, 'path': {'wildcard': '*'}}})
  return resList

def makeFilter(word):
    return {'text': {'query': word, 'path': {'wildcard': '*'}}}

def makeQuery(master,words = ' '):
    pipeline = [
    {
        '$search': {
            'index': 'syllabusSearchIndex', 
            'compound': {
                'must': [
                    {
                        'text': {
                            'query': master, 
                            'path': {
                                'wildcard': '*'
                            }
                        }
                    }
                ], 
                'should': [
                    # Generated filter goes inside here
                ], 
                'minimumShouldMatch': 1
            },
            'highlight':{'path':{'wildcard':'*'}}
        }
    },{'$limit':5},{
        '$project': {
            '_id': 0, 
            'regno':1,
            'highlights': { '$meta': 'searchHighlights' },
            'score': {'$meta': 'searchScore'}
        }
    }#,{'$match':{'score':{'$gt':2.5}}} #more for japanese but needs tuning
    ]
    target = pipeline[0]['$search']['compound']['should']

    for word in words:
        target.append(makeFilter(word))
    return pipeline
