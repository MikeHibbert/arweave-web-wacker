import json
import requests
import logging
import hashlib
from jose import jwk
from jose.utils import base64url_encode, base64url_decode, base64
from jose.backends.cryptography_backend import CryptographyRSAKey
from utils import (
    winston_to_ar, 
    ar_to_winston, 
    owner_to_address,
    create_tag,
    decode_tag
)

logger = logging.getLogger(__name__)

class Wallet(object):
    HASH = 'sha256'

    def __init__(self, jwk_file='jwk_file.json'):
        with open(jwk_file, 'r') as j_file:
            self.jwk_data = json.loads(j_file.read())
            self.jwk = jwk.construct(self.jwk_data, algorithm="RS256")
            jwk.ALGORITHMS
            self.owner = self.jwk_data.get('n')
            self.address = owner_to_address(self.owner)

        self.api_url = "https://arweave.net"
        self.balance = 0
        
    def get_balance(self):
        url = "{}/wallet/{}/balance".format(self.api_url, self.address)

        response = requests.get(url)

        if response.status_code == 200:
            self.balance = winston_to_ar(response.text)

        return self.balance  
    
    def sign(self, message):
        crypto_key = CryptographyRSAKey(self.jwk_data)
        
        return crypto_key.sign(message).encode()
    
    def get_last_transaction_id(self):
        url = "{}/wallet/{}/last_tx".format(self.api_url, self.address)

        response = requests.get(url)

        if response.status_code == 200:
            self.last_tx = winston_to_ar(response.text)
            
        return self.last_tx


class Transaction(object):
    def __init__(self, jwk_data, wallet, **kwargs):
        self.jwk_data = jwk_data
        self.jwk = jwk.construct(self.jwk_data, algorithm="RS256")
        
        self.id = ''
        self.last_tx = wallet.get_last_transaction_id()
        self.owner = self.jwk_data.get('n')
        self.tags = []
        self.quantity = kwargs.get('quantity', '0')
        self.data = kwargs.get('data', '').encode('ascii')
        self.target = kwargs.get('target', '')
        
        reward = kwargs.get('reward', None)
        if reward != None:
            self.reward = reward  
        else:
            self.reward = self.get_reward(self.data)
            
        self.signature = ''
        
    def get_reward(self, data, target_address=None):
        data_length = len(data)
        
        url = "/price/{}".format(data_length)
        
        if target_address:
            url = "/price/{}/{}".format(data_length, target_address)

        response = requests.get(url)

        if response.status_code == 200:
            reward = response.text
            
        return reward       
    
    def add_tag(self, name, value):
        tag = create_tag(name, value)
        self.tags.append(tag)        
        
    def sign(self, wallet):
        data_to_sign = self.get_signature_data()
        
        raw_signature = wallet.sign(data_to_sign)
        
        self.signature = base64url_encode(raw_signature)
        
        self.id = hashlib.sha256(raw_signature).digest()
        
    def get_signature_data(self):
        tag_str = ""
        
        for tag in self.tags:
            name, value = decode_tag(tag)
            tag_str += "{}{}".format(name, value)
            
        owner = base64url_decode(self.jwk_data['n'])
        target = base64url_decode(self.target)
        data = base64url_decode(self.data)
        quantity = self.quantity.encode()
        reward = self.reward.encode()
        last_tx = self.last_tx.encode()
        
        return tag_str.encode() + owner + target + data + quantity + reward + last_tx
    
    def post(self):
        url = "{}/tx".format(self.api_url)

        response = requests.post(url, data=self.json_data)

        if response.status_code == 200:
            self.last_tx = winston_to_ar(response.text)
            
        return self.last_tx    
    
    @property
    def json_data(self):
        return json.dumps({
         'data': self.data,
         'id': self.id,
         'last_tx': self.last_tx,
         'owner': self.owner,
         'quantity': self.quantity,
         'reward': self.reward,
         'signature': self.signature,
         'tags': self.tags,
         'target': self.target
        })
        

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    
    def run_test(jwk_file):
        wallet = Wallet(jwk_file)

        balance = wallet.get_balance()
        
        logger.debug(balance)

    run_test("/home/mike/Dropbox/hit solutions/Bitcoin/Arweave/arweave-keyfile-OFD5dO06Wdurb4w5TTenzkw1PacATOP-6lAlfAuRZFk.json")

