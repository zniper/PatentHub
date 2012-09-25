from pyquery import PyQuery as pq
import requests
import Queue
import threading
import datetime
import logging
import time

#logging.basicConfig(filename='/var/log/pse.log', filemode='a')
log = logging.getLogger(__name__)

#GOOGLE_URL = 'http://www.google.com/search?sclient=psy-ab&hl=en&safe=off&site=&tbm=pts&source=hp&q=%s&btnG=Search&num=20'
GOOGLE_URL = 'http://www.google.com/search?num=%(num)s&hl=en&safe=off&tbm=pts&q=%(kw)s&oq=%(kw)s&start=%(start)s'
G_PATENT_URL = 'www.google.com/patents/%s'

queue_stack = []
result_stack = {}
patent_list = []
threads = []

class PatentItem():
    pid = ''
    title = ''
    description = ''
    url = ''
    pdf = ''
    source = ''


class ThreadUrl(threading.Thread):
    
    def getSinglePatentInfo(self, url, pid=''):
        if not url:
            pURL = G_PATENT_URL % pid
        else:
            pURL = url
        abstract = ''
        retry = 03
        while retry > 0:
            try:
                p0 = pq(requests.get(pURL).text)
                table = p0('#summarytable')
                abstract = table('.patent_abstract_text').text()
            except:
                print 'Error when getting single patent info'
            retry -= 1
        return {'abstract':abstract}

    def __init__(self, pid):
        threading.Thread.__init__(self)
        self.pid = pid

    def run(self):
        global queue_stack
        global result_stack
        while True:
            time.sleep(0.5)
            if len(queue_stack) > 0:
              #print '[%s] getting' % self.pid
              try:
                queue = queue_stack[0]
                if queue.empty():
                    #print '[%s] do nothing' % self.pid
                    continue
                print '[%s] in progress' % self.pid
                patent = queue.get()
                patent.description = self.getSinglePatentInfo(patent.url)['abstract']
                result_stack[queue].append(patent)
                print '[%s] completed' % self.pid
                queue.task_done()
              except:
                print 'error with thread ' + self.pid
            else:
                pass
            

class GooglePatent():

    _kw = ''
    _num = '10'
    _start = ''
    stats = ''

    def __init__(self, **kwargs):
        self._kw = kwargs.get('keyword', '')
        self._num = kwargs.get('ipp', '10')
        self._start = kwargs.get('page', '')
        try:
            self._start = int(start-1)*int(self._num)
        except:
            pass

    def getAllPatentInfo(self, patent_list):
        details = []
        for item in patent_list:
            entry = getSinglePatentInfo(item.url)
            details.append(entry)
        return details


    def performSearch(self):
        print 'start searching'
        queue = Queue.Queue()
        temp_list = []
        retry = 03
        item_number = ''
        while retry > 0:
            try:
                # the the result list first
                req = requests.get(GOOGLE_URL % {'kw'    : self._kw,
                                                 'num'   : self._num,
                                                 'start' : self._start})
                #page = requests.get('http://www.google.com/search?sclient=psy-ab&hl=en&safe=off&site=&tbm=pts&source=hp&q=mobile&btnG=Search')
                p0 = pq(req.text)
                print 'get the first page'
                # sample data	
                #f0 = open('sample.html', 'r')
                #p0 = pq(f0.read())
                #f0.close()
                # end of sample content
                res = p0('div#ires')
                # get the general stats, result number
                statz = p0('div#resultStats')
                try:
                    statz.children().remove()
                except:
                    pass
                self.stats = statz.text()
                # get all the items in page
                if res:
                    items = res('li.g')
                    for item in items:
                      try:
                        pqi = pq(item)
                        oPatent = PatentItem()
                        oPatent.title = pqi('h3').text()
                        oPatent.url = pqi('table.ts cite.kv').text().strip()
                        if oPatent.url.lower().find('http://') != 0:
                            oPatent.url = 'http://' + oPatent.url
                        while oPatent.url[-1] == '/':
                            oPatent.url = oPatent.url[:-1]
                        oPatent.pid = oPatent.url[oPatent.url.rindex('/')+1:]
                        oPatent.pdf = oPatent.url + '.pdf'
                        oPatent.source = 'Google Patents'
                        #p_details = self.getSinglePatentInfo(oPatent.url)
                        #oPatent.description = p_details['abstract']
                        temp_list.append(oPatent)
                      except:
                        # do not include error item
                        pass
                    break
                else:
                    print 'Cannot find result content. Retrying... ' + str(retry)
            except:
                print 'There is error when getting Google search result.'
            retry -= 1


        # collect all descriptions in separate phase
        print 'start collecting descriptions'
        for item in temp_list:
            queue.put(item)
        global queue_stack
        global result_stack
        queue_stack.append(queue)
        result_stack[queue] = []
        queue.join()
        queue_stack.remove(queue)
        print 'searching done'

        # correct order of resulted items
        temp_result = result_stack[queue]
        result_stack.pop(queue)
        final_result = []
        for pi in temp_list:
            for item in temp_result:
              try:
                if item.pid.lower() == pi.pid.lower():
                    final_result.append(item)
                    temp_result.remove(item)
                    break
              except:
                log.error('Error when sorting an item')
        print 'sorting done'

        return final_result


for ti in range(10):
    thread = ThreadUrl(str(ti))
    threads.append(thread)
    thread.setDaemon(True)
    thread.start()

#print datetime.datetime.now()
#a = GooglePatent('mobile')
#a.performSearch()
#print patent_list
#print datetime.datetime.now()
