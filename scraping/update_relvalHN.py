# Updates relvalHN.html

import requests, sys, HNinfo
requests.packages.urllib3.disable_warnings()

# Initialize
HNsession = HNinfo.HNlogin()
HN_RELVAL_URL = 'https://hypernews.cern.ch/HyperNews/CMS/get/relval.html'
out = open('relvalHN.html','w')
page = HNsession.get(HN_RELVAL_URL).content
out.write(page)

out.close()