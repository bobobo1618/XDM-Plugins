from xdm.plugins import *
import requests
import re
import xml.etree.ElementTree as etree

size_exp = re.compile('([0-9\.]+) (K|M|G|T)iB')

sizemult = {
    'K': 1024,
    'M': 1024**2,
    'G': 1024**3,
    'T': 1024**4
}

def findSize(desc):
    match = size_exp.search(desc)
    
    if match:
        try:
            return float(match.group(1)) * sizemult[match.group(2)]
        except:
            return None

    return None

class Nyaa(Indexer):
    version = '0.1'
    identifier = 'com.github.bobobo1618.nyaa'
    types = ['de.lad1337.torrent']

    _config = {}
    config_meta = {
        'plugin_meta': 'Anime Nyaatorrents indexer'
    }

    def searchForElement(self, element):
        #import ipdb; ipdb.set_trace()
        payload = {
            'page':'rss',
            'cats':'1_37',
        }

        terms = element.getSearchTerms()

        downloads = []

        for term in terms:
            payload['term'] = term
            r = requests.get('http://nyaa.se/', params=payload)
            log('Nyaa search for term %s : %s' % (term, r.url))
            
            try:
                xml = etree.fromstring(r.text.encode("utf-8"))
                items = xml.findall("channel/item")
            except:
                log.error('Error loading nyaa.')
                continue

            for item in items:
                title = item.find('title').text

                if "- {:>02}".format(element.number) not in title:
                    continue

                url = item.find("link").text
                ex_id = re.search("tid=(\d+)", url).group(1)
                
                desc = item.find('description')
                curSize = findSize(desc).text

                if not curSize:
                    log("Could not find size in: %s" % desc.text)
                    continue

                log("%s found on Fanzub: %s" % (element.type, title))
                d = Download()
                d.url = url
                d.name = title
                d.element = element
                d.size = curSize
                d.external_id = ex_id
                d.type = 'de.lad1337.torrent'
                downloads.append(d)

        return downloads