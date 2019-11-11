import sys
import json
import requests
import logging
import arrow
from bs4 import BeautifulSoup 
from urllib.parse import urlparse
from arweave import Wallet, Transaction, TRANSACTION_DATA_LIMIT_IN_BYTES

logger = logging.getLogger(__name__)

class WebWhacker(object):
    def __init__(self, wallet, url, depth=2):
        self.wallet = wallet
        
        root_resp = requests.get(url)
        
        if root_resp.status_code == 200:
            self.root = soup = BeautifulSoup(root_resp.content, 'html5lib')
            root_uri = urlparse(url)   
            
            self.project = { "root_url": root_uri.netloc, "pages": [] }
            
            if len(root_resp.text) < TRANSACTION_DATA_LIMIT_IN_BYTES:
                self.project['pages'].append({
                 "path": root_uri.path,
                 "data": root_resp.text,
                 "transaction_id": ""
                })
                
            else:
                raise Exception("Root page {} is too large to backup to the blockchain!".format(url))
            
        else:
            raise Exception("Unable to connect to {}".format(url))
        
        for anchor in self.root.findAll('a'):
            url = anchor.get('href', '')
            
            if root_uri.netloc in url or url.startswith('/'):
                
                if url.startswith('/'):
                    url = "{}://{}{}".format(root_uri.scheme, root_uri.netloc, url)
                    
                response = requests.get(url)
                
                if response.status_code == 200:   
                    if len(response.text) < TRANSACTION_DATA_LIMIT_IN_BYTES:
                        parsed_uri = urlparse(url)
                        
                        self.project['pages'].append({
                         "path": parsed_uri.path,
                         "data": response.text,
                         "transaction_id": ""
                        })                    
                
    def save_to_blockchain(self):
        for page in self.project['pages']:
            try:
                data = page['data']
                tx = Transaction(self.wallet, data=data.encode())
                tx.add_tag("app", "Arweave-webwhacker")
                tx.add_tag('created', str(arrow.now().timestamp))
                tx.add_tag('url', self.project['root_url'])
                tx.add_tag('path', page['path'])
                
                tx.sign(self.wallet)
                tx.post()
            
                page['transaction_id'] = tx.id.decode()
            except Exception as e:
                logger.debug(e)
            
        self.save_project_json()
    
    
    def save_project_json(self):
        json_output = json.dumps(self.project, indent=4, sort_keys=True)
        output_filename = "wwproj-{}-{}.json".format(self.project.get('root_url'), arrow.now().timestamp)
        
        with open(output_filename, "w") as opf:
            opf.write(json_output)
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    depth = 2
    if len(sys.argv) < 3:
        print("Not engough arguments no URL or wallet file supplied")
        
    if len(sys.argv) > 3:
        depth = int(sys.argv[3])
        
    wallet = Wallet(sys.argv[2])
        
    ww = WebWhacker(wallet, sys.argv[1], depth=depth)
    ww.save_to_blockchain()