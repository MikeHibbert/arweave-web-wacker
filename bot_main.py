import sys
import requests
import logging
from arweave import Wallet, Transaction, TRANSACTION_DATA_LIMIT_IN_BYTES

logger = logging.getLogger(__name__)

def backup_url(url, depth=2):
    root = requests.get(url)
    
    if root.status_code == 200:
        logger.debug(root.text)
        
    else:
        raise Exception("Unable to connect to {}".format(url))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    depth = 2
    if len(sys.argv) < 3:
        print("Not engough arguments no URL or wallet file supplied")
        
    if len(sys.argv) > 3:
        depth = int(sys.argv[2])
        
    backup_url(sys.argv[1], depth=depth)