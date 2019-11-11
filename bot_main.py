import sys
import requests

def backup_url(url, depth=2):
    root = requests.get(url)
    
    if root.status_code == 200:
        
        
    else:
        raise Exception("Unable to connect to {}".format(url))


if __name__ == "__main__":
    depth = 2
    if len(sys.argv > 2):
        depth = int(sys.argv[2])
        
    backup_url(sys.argv[1], depth=depth)