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
    tmpList = [] #should result in list of dict like elments?
    for x in mydoc:
        tmpList.append(x)
    
    resList = extractDataFromList(tmpList)


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
    # query 
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
    },{'$limit':100},{
        '$project': {
            '_id': 0, 
            'regno':1,
            'highlights': { '$meta': 'searchHighlights' },
            'score': {'$meta': 'searchScore'}
        }
    }#,{'$match':{'score':{'$gt':2.5}}} #more for japanese but needs tuning
    ]

    # add in additional arguments
    target = pipeline[0]['$search']['compound']['should']
    for word in words:
        target.append(makeFilter(word))
    return pipeline


def extractDataFromList(argList):
    returnList =[]

    for i in range(len(argList)):
        elmDict = argList[i] # this would be {'regno':'regnostring','highlights':[highlights],'score':number}
        storageDict = {'regno':elmDict['regno'],'score':elmDict['score'],'sumscore':0,'sumlabel':[],'results':[]}


        for x in elmDict['highlights']:
            storageDict['sumlabel'] += [x['path']]
            storageDict['sumscore'] += x['score']
            concatStr = ""
            for j in range(len(x['texts'])):# x['texts'] should return [{'value':str},{'value':str},{'value':str}]  
                if x['texts'][j]['type'] == "hit":
                    concatStr += '<span style=\"color:red\">'+x['texts'][j]['value']+'</span>'
                else:
                    concatStr += '<span>'+x['texts'][j]['value']+'</span>'
            storageDict['results'] += ['...'+concatStr+'... ']
        returnList.append(storageDict) # returns list

    # what we want to return
    #[{
    #    'regno':'something',
    #    'labels':[labels,labels,labels],
    #    'results':['before<h3>hit</h3>after','before<h3>hit</h3>after','before<h3>hit</h3>after']
    #},{
    #    'regno':'something',
    #    'labels':[labels,labels,labels],
    #    'results':['before<h3>hit</h3>after','before<h3>hit</h3>after','before<h3>hit</h3>after']
    #},{
    #    'regno':'something',
    #    'labels':[labels,labels,labels],
    #    'results':['before<h3>hit</h3>after','before<h3>hit</h3>after','before<h3>hit</h3>after']
    #},{
    #    'regno':'something',
    #    'labels':[labels,labels,labels],
    #    'results':['before<h3>hit</h3>after','before<h3>hit</h3>after','before<h3>hit</h3>after']        
    #}]
    return argList

