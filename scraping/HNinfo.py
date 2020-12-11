import requests

UserID = ''
Password = ''

def getAddress(line,start='http',stop='.html',includeEnd=True):
    http_loc = line.find(start)
    if includeEnd: html_loc = line.find(stop)+len(stop)
    else: html_loc = line.find(stop)
    return line[http_loc:html_loc]

def HNlogin():
    login_payload = {
        "UserID": UserID,
        "Password": Password
    }
    HN_POST_URL = 'https://hypernews.cern.ch/HyperNews/CMS/login.pl'

    session = requests.Session()
    session.post(HN_POST_URL, data=login_payload, verify=False)
    return session