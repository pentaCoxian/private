import json
from pymongo import MongoClient
import bson
import pymongo
import certifi
import urllib.parse

def application(environ, start_response):
    headers = [('Content-Type', 'application/json')]
    start_response('200 OK', headers)

    dbname = get_database()
    cols = dbname["courseOfferings"]
    testStr = str(urllib.parse.unquote(environ['QUERY_STRING']))
    if testStr == '':
        testStr = ' '
    pipeline = [
  {
    '$search': {
      'index': 'courseSearchIndex',
      'text': {
        'query': testStr,
        'path': {
          'wildcard': '*'
        }
      }
    }
  }
]


    mydoc = cols.aggregate(pipeline)
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

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING, tlsCAFile=ca)

    # Create the database for our example (we will use the same database throughout the tutorial
    return client['icu']
