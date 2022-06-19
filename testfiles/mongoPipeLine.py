def makeFilter(word):
    return {'text': {'query': word, 'path': {'wildcard': '*'}}}

def makeQuery(master,words):
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
    }, {'$limit':5
    },{
        '$project': {
            'id': 0, 
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
