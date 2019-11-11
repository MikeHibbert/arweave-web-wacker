import sys
import json
import logging
from arweave import Wallet, Transaction, TRANSACTION_DATA_LIMIT_IN_BYTES

logger = logging.getLogger(__name__)

def check_and_report_status(wallet, project_file):
    with open(project_file, 'r') as prj_file:
        project = json.loads(prj_file.read())
        
        logger.info("ROOT URL:".format(project.get('root_url')))
        
        for page in project.get('pages'):
            tx = Transaction(wallet, id=page['transaction_id'].encode())
            status = tx.get_status()
            
            path = page['path'] if len(page['path']) > 0 else '/'
            
            logger.info("URL: '{}'\nSTATUS:{}".format(path, status))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) < 3:
        print("Not engough arguments no project or wallet files supplied")
        
    wallet = Wallet(sys.argv[1])
    
    check_and_report_status(wallet, sys.argv[2])