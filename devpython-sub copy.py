import json
from pymongo import MongoClient
import bson
import pymongo
import certifi
import urllib.parse

# wsgi entry point
def application(environ, start_response):
    # send back respond headders, selecting type json and also allowing http_host of icu-syllabus.com to use this script with out triggering cors policy
    originSite = 'icu-syllabus.com'
    headers = [('Content-Type', 'application/json; charset=utf-8'),('Access-Control-Allow-Origin',originSite)]
    start_response('200 OK', headers)

    # connect to mongodb
    dbname = get_database()

    # get params from url(also pharse encoded japanese)
    inputwords = str(urllib.parse.unquote(environ['QUERY_STRING'])).split("+")

    # tune for match (needs tuning)
    minMatch = len(inputwords) -1

    # make Qaurry from input (if theres no parameters, make it a whitespace to avoid errors)
    for i in range(len(inputwords)):
        if inputwords[i] == '':
            inputwords[i] = ' '
    pipeline = makeQuery(inputwords[0],inputwords[1:])

    # set target and aggregate
    cols = dbname["courseSyllabus"]
    mydoc = cols.aggregate(pipeline)

    # convert to list
    resList = [] #should result in list of dict like elments?
    for x in mydoc:
        resList.append(x)
    


    # convert to json
    res = json.dumps(resList,ensure_ascii=False).encode('utf-8')
    return [res]

# connet to mongodb and open database, then select icu
def get_database():
    from pymongo import MongoClient
    import pymongo
    import certifi
    ca = certifi.where()

    CONNECTION_STRING = "mongodb+srv://python:lolpython556@pythondev.etdrtaj.mongodb.net/pythondev"
    client = MongoClient(CONNECTION_STRING, tlsCAFile=ca)

    return client['icu']


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

