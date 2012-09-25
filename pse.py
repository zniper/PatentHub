import google
import simplejson as json
from flask import Flask, request
import logging

#logging.basicConfig(filename = '/var/log/pse.log', 
#                   filemode = 'a',
#                   level = logging.DEBUG)
log = logging.getLogger(__name__)
app = Flask(__name__)

@app.route('/query/<keyword>')
def queryPatent(keyword):
    ipp = request.args.get('ipp', '10')
    page = request.args.get('page', '')
    ge = google.GooglePatent(keyword = keyword, 
                             ipp     = ipp,
                             page    = page)
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
    result.append({'stats':ge.stats})
    log.info('Return result')
    return json.dumps(result)

if __name__ == '__main__':
    app.run()

