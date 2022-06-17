import json
import re
from pymongo import MongoClient
import bson
import pymongo
import certifi
from urllib.parse import quote
import urllib.parse


# wsgi entry point
def application(environ, start_response):
    # send back respond headders, selecting type json and also allowing http_host of icu-syllabus.com to use this script with out triggering cors policy
    originSite = 'icu-syllabus.com'
    headers = [('Content-Type', 'application/json; charset=utf-8'),('Access-Control-Allow-Origin','*')]
    start_response('200 OK', headers)

    # connect to mongodb
    dbname = get_database()
    cols = dbname["courseSyllabus"]
    
    # get params from url(also pharse encoded japanese)
    inputwords = str(urllib.parse.unquote(environ['QUERY_STRING'])).split("+")
    minMatch = len(inputwords) -1
    # make Qaurry from input (if theres no parameters, make it a whitespace to avoid errors)
    for i in range(len(inputwords)):
        if inputwords[i] == '':
            inputwords[i] = ' '
    pipeline = makeQuery(inputwords[0],inputwords[1:],minMatch)
    # set target and aggregate
    mydoc = cols.aggregate(pipeline)

    # convert to list
    tmpList = [] #should result in list of dict like elments?
    for x in mydoc:
        tmpList.append(x)

    # convert to json
    resList = extractDataFromList(tmpList)
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

def makeQuery(master,words = 'a',minMatch=0):
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
                'minimumShouldMatch': minMatch
            },
            'highlight':{'path':{'wildcard':'*'}}
        }
    },{'$limit':50},{
        '$lookup':{
            'from': 'courseOfferings',
            'localField': '_id',
            'foreignField': '_id',
            'as': 'mera'
        }
    },{
        '$project': {
            '_id': 0, 
            'regno':1,
            'highlights': { '$meta': 'searchHighlights' },
            'score': {'$meta': 'searchScore'},
            'mera':1
        }
    }#,{'$match':{'score':{'$gt':2.5}}} #more for japanese but needs tuning
    ]
    target = pipeline[0]['$search']['compound']['should']

    for word in words:
        target.append(makeFilter(word))
    return pipeline


def extractDataFromList(argList):
    returnList =[]
    for i in range(len(argList)):
        
        elmDict = argList[i] # this would be {'regno':'regnostring','highlights':[highlights],'score':number}
        storageDict = {
            'regno':elmDict['regno'],
            'course_no':elmDict['mera'][0]['course_no'],
            'title_e':elmDict['mera'][0]['title_e'],
            'title_j':elmDict['mera'][0]['title_j'],
            'score':elmDict['score'],
            'results':[]
        }
        url = 'https://campus.icu.ac.jp/public/ehandbook/PreviewSyllabus.aspx?regno='+elmDict['regno']+'&year=2022&term='+elmDict['regno'][0]
        for x in elmDict['highlights']:
            concatStr = ""
            flag = True
            for j in range(len(x['texts'])):# x['texts'] should return [{'value':str},{'value':str},{'value':str}]  
                param = '#:~:text='
                target = x['texts']
                # generate link first
                # https://example.com#:~:text=prefix-,startText,endText,-suffix
                if target[j]['type'] == 'hit':
                    try:
                        param += conv(target[j-1]['value'].strip(),-1)+quote(target[j]['value'].strip())+conv(target[j+1]['value'].strip(),0)
                    except IndexError:
                        try:
                            param += quote(target[j]['value'].strip())+conv(target[j+1]['value'].strip(),0)
                        except IndexError:
                            param += conv(target[j-1]['value'].strip(),-1)+quote(target[j]['value'].strip())
                    # join the parameters to make a string with href
                    concatStr += '<a href="'+url+param+'">'+target[j]['value']+'</a>'
                else:
                    # if not a hit word, just add to string
                    #concatStr += '<span>'+target[j]['value']+'</span>'
                    concatStr += '<span>'+target[j]['value'].lstrip('　').lstrip('.,')+'</span>'
            storageDict['results'] += ['<div class ="syAb">'+concatStr+'...</div><br>']
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
    return returnList

def conv(targetItem,order):
    input = re.split('[\',;/\-、，(, )]',targetItem)[order]#[\'(, ),;/-、，(\- )]
    ret = ''
    if input != '':
        if order == -1:
            ret = quote(input) + '-,'
        else:
            ret = ',-' + quote(input)
    return ret