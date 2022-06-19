import json
import re
from pymongo import MongoClient
import bson
import pymongo
import certifi
from urllib.parse import quote
import urllib.parse

# wsgi entry point
# Accessed by https://icu-syllabus.com/python-file-name.py
def application(environ, start_response):
    # send back respond headders, selecting type json and also allowing http_host of icu-syllabus.com to use this script with out triggering cors policy
    originSite = 'icu-syllabus.com'
    headers = [('Content-Type', 'application/json; charset=utf-8'),('Access-Control-Allow-Origin',originSite)]
    start_response('200 OK', headers)

    # connect to mongodb
    dbname = get_database()
    cols = dbname["courseSyllabus"]
    
    # get params from url(also pharse encoded japanese)
    inputwords = str(urllib.parse.unquote(environ['QUERY_STRING'])).split("+")

    # make Qaurry from input (if theres no parameters, make it a whitespace to avoid errors)
    minMatch = len(inputwords) -1
    for i in range(len(inputwords)):
        if inputwords[i] == '':
            inputwords[i] = ' '
    # pass in arguments to query
    pipeline = makeQuery(inputwords[0],inputwords[1:],minMatch)
    # set target and aggregate
    mydoc = cols.aggregate(pipeline)

    # convert answer to list
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

    # connect to db, select collection icu
    CONNECTION_STRING = "mongodb+srv://python:lolpython556@pythondev.etdrtaj.mongodb.net/pythondev"
    client = MongoClient(CONNECTION_STRING, tlsCAFile=ca)
    return client['icu']


def makeFilter(word):
    return {'text': {'query': word, 'path': {'wildcard': '*'}}}

# make query pipleline from arguments
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

# Read results and reshape to 
def extractDataFromList(argList):
    returnList =[]

    for i in range(len(argList)):
        elmDict = argList[i] # this would be {'regno':'regnostring','highlights':[highlights],'score':number}

        # Dictionary to return
        storageDict = {
            'regno':elmDict['regno'],
            'course_no':elmDict['mera'][0]['course_no'],
            'title_e':elmDict['mera'][0]['title_e'],
            'title_j':elmDict['mera'][0]['title_j'],
            'score':elmDict['score'],
            'results':[]
        }

        # Generate syllabus url
        url = 'https://campus.icu.ac.jp/public/ehandbook/PreviewSyllabus.aspx?regno='+elmDict['regno']+'&year=2022&term='+elmDict['regno'][0]
        
        # Loop through result, adding html tags and urls that point to result on syllabus
        for x in elmDict['highlights']:
            concatStr = ""
            for j in range(len(x['texts'])):# x['texts'] should return [{'value':str},{'value':str},{'value':str}]  
                param = '#:~:text='
                target = x['texts']

                # Try generating link using #:~:text=prefix-,startText,endText,-suffix syntax
                if target[j]['type'] == 'hit':
                    try:
                        # both before and after strings are present
                        param += conv(target[j-1]['value'].strip(),-1)+quote(target[j]['value'].strip())+conv(target[j+1]['value'].strip(),0)
                    except IndexError:
                        try:
                            # only front element
                            param += quote(target[j]['value'].strip())+conv(target[j+1]['value'].strip(),0)
                        except IndexError:
                            # only before element
                            param += conv(target[j-1]['value'].strip(),-1)+quote(target[j]['value'].strip())
                            
                    # join the parameters to make a string with href
                    concatStr += '<a href="'+url+param+'">'+target[j]['value']+'</a>'
                else:
                    # if not a word(type="hit"), just add to string
                    concatStr += '<span>'+target[j]['value'].lstrip('　').lstrip('.,')+'</span>'


            storageDict['results'] += ['<div class ="syAb">'+concatStr+'...</div><br>']
        returnList.append(storageDict)
    return returnList

def conv(targetItem,order):
    #remove chars that interfere with text fragmentation by regex
    input = re.split('[\',;/\-、，(, )]',targetItem)[order]
    ret = ''
    if input != '':
        if order == -1:
            ret = quote(input) + '-,'
        else:
            ret = ',-' + quote(input)
    return ret