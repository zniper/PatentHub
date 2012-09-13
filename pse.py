import google
import simplejson as json
from flask import Flask
import logging

#logging.basicConfig(filename = '/var/log/pse.log', 
#                   filemode = 'a',
#                   level = logging.DEBUG)
log = logging.getLogger(__name__)
app = Flask(__name__)

@app.route('/query/<keyword>')
def queryPatent(keyword):
    ge = google.GooglePatent(keyword)
    log.info('Get the request')
    items = ge.performSearch()
    result = []
    for item in items:
        idict = {}
        idict['id'] = item.pid
        idict['title'] = item.title
        idict['description'] = item.description
        idict['source'] = item.source
        idict['pdf'] = item.pdf
        result.append(idict)
    log.info('Return result')
    return json.dumps(result)

if __name__ == '__main__':
    app.run()

