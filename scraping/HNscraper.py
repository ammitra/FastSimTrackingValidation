# Usage as 
# grep '<text in post title>' | python HNscraper.py
# Must fill in UserID and Password in HNinfo.py for hypernews
import requests, sys, HNinfo, optparse
requests.packages.urllib3.disable_warnings()

parser = optparse.OptionParser()
# Require input
parser.add_option('--find', metavar='F', type='string', action='store',
                default =   'BulkGrav',
                dest    =   'find',
                help    =   'String to find')
(options,args) = parser.parse_args()
TO_FIND = options.find

# Get everything from stdin
addresses = []
for p in sys.stdin:
    addresses.append(HNinfo.getAddress(p))
for p in args:
    addresses.append(p)

# Initialize
dmytro_addresses = []
HNsession = HNinfo.HNlogin()
# Loop over addresses and look for TO_FIND
for addr in addresses:
    print ('Checking '+addr)
    action = addr[addr.find('/HyperNews'):addr.find('.html')+len('.html')]
    page = HNsession.get(addr).content

    if TO_FIND in page:
        print ('FOUND: '+ addr)

    # If you can't find it, save dmytro address
    else:
        for line in page.split('\n'):
            if line == '': continue
            if 'dmytro' in line:
                dmytro_addresses.append(HNinfo.getAddress(line,stop='">https',includeEnd=False))

# Check the contents of dmytro pages
print ('Checking more...')
for daddr in dmytro_addresses:
    page = requests.get(daddr,verify=False).content
    if TO_FIND in page:
        print ('FOUND: '+ daddr)