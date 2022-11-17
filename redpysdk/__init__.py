import requests
import logging
import time

from .settings import REDDIO_ENDPOINT_TESTNET, REDDIO_ENDPOINT_MAINNET

from .http_utils import request
from .starkex_utils import get_signature_local,get_asset_id
from .signature import get_random_private_key,private_to_stark_key

class Reddio(object):
    def __init__(self, env="testnet"):
        self.env = env
        if self.env == "testnet":
            self.endpoint = REDDIO_ENDPOINT_TESTNET
        elif self.env == "mainnet":
            self.endpoint = REDDIO_ENDPOINT_MAINNET

    def get_vault_id(self, stark_key, assetid):
        data = {"asset_id":assetid, "stark_keys": stark_key}
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url = '%s/v1/vaults' % self.endpoint, params = data, headers = headers)
        vault_id = r.json()['data']['vault_ids'][0]
        return vault_id
    
    def get_stark_key_pair(self):
        priv_key = get_random_private_key()
        stark_key = hex(private_to_stark_key(priv_key))
        return stark_key, hex(priv_key)
    
    def get_stark_key_by_private_key(self, stark_private_key):
        return hex(private_to_stark_key(int(stark_private_key, 16)))

    def get_order_info(self, stark_key, contract1Type, contract1Address, contract1TokenID, contract2Type, contract2Address, contract2TokenID):
        uri = '/v1/order/info' + '?stark_key=' + str(stark_key) + '&contract1=' + str(contract1Type) + ':' + str(contract1Address) + ':' + str(contract1TokenID) + '&contract2=' + str(contract2Type) + ':' + str(contract2Address) + ':' + str(contract2TokenID)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers)
        return r.json()['data']


    def get_balances(self, stark_key, page=1, limit=10):
        uri = '/v1/balances' + '?stark_key=' + str(stark_key) + '&page=' + str(page) + '&limit=' + str(limit)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json', "User-Agent":"ReddioFrame"}
        r = requests.get(url, headers = headers)
        return r.json()["data"]["list"]

    def get_orders(self, contract_address):
        uri = '/v1/orders' + '?contract_address=' + str(contract_address)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers)
        order_list = []
        for order in r.json()["data"]["list"]:
            if order["stark_key"] != "":
                order_list.append(order)
        return order_list

    def list_nft_by_user(self, stark_key, contract_address):
        uri = '/v1/balances' + '?stark_key=' + str(stark_key) + '&contract_address=' + str(contract_address) + '&limit=1000'
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers)
        return r.json()["data"]["list"]

    def list_user_nfts(self, stark_key, contract_address):
        nfts = self.list_nft_by_user(stark_key, contract_address)
        nft_list = []
        for nft in nfts:
            if nft["balance_available"] > 0 and int(nft["token_id"]) > 668:
                nft_list.append(nft)
        return nft_list

    def get_nonce(self, stark_key):
        """
        Gets the nonce for a given stark key.
        """
        data = {"stark_key": stark_key}
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url = '%s/v1/nonce' % self.endpoint , params = data, headers = headers)
        return r.json()['data']['nonce']
    
    def transferNFT(self, stark_private_key, sender_starkkey, receiver, token_type, contract, tokenID, expiration_timestamp=4194303):
        quantum = 1
        asset_id =  hex(get_asset_id(token_type, contract, quantum, int(tokenID)))
        vault_id = self.get_vault_id(sender_starkkey, asset_id)
        receiver_vault_id = self.get_vault_id(receiver, asset_id)
        nonce = self.get_nonce(sender_starkkey)
        data = {}
        data['asset_id'] = str(asset_id)
        data['receiver_vault_id'] = str(receiver_vault_id)
        data['sender_vault_id'] = str(vault_id)
        data['nonce'] = str(nonce)
        data['sender_private_key'] = str(stark_private_key)
        data['amount'] = "1"
        data['receiver'] = str(receiver)
        data['expiration_timestamp'] = str(expiration_timestamp)
        data['stark_key'] = str(sender_starkkey)

        transfer_data = get_transfer_data(data)

        url = self.endpoint + '/v1/transfers'
        headers = {'Content-Type': 'application/json'}
        x = request(url, transfer_data, headers)
        return x.json()
    
    def get_contract_info(self, contract_address):
        uri = '/v1/contract_info' + '?contract_address=' + str(contract_address)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers)
        return r.json()['data']
    
    def transferFT(self, stark_private_key, sender_starkkey, receiver, token_type, contract, amount, expiration_timestamp=4194303):
        contract_info = self.get_contract_info(contract)
        quantum = int(contract_info["quantum"])
        decimals = int(contract_info["decimals"])
        asset_id =  hex(get_asset_id(token_type, contract, quantum, 1))
        vault_id = self.get_vault_id(sender_starkkey, asset_id)
        receiver_vault_id = self.get_vault_id(receiver, asset_id)
        nonce = self.get_nonce(sender_starkkey)
        data = {}
        amount = int(int(float(amount) * int(10 ** decimals)) / int(quantum))
        data['asset_id'] = str(asset_id)
        data['receiver_vault_id'] = str(receiver_vault_id)
        data['sender_vault_id'] = str(vault_id)
        data['nonce'] = str(nonce)
        data['sender_private_key'] = str(stark_private_key)
        data['amount'] = str(int(amount))
        data['receiver'] = str(receiver)
        data['expiration_timestamp'] = str(expiration_timestamp)
        data['stark_key'] = str(sender_starkkey)

        transfer_data = get_transfer_data(data)

        url = self.endpoint + '/v1/transfers'
        headers = {'Content-Type': 'application/json'}
        while True:
            try:
                response = request(url, transfer_data, headers)
                sequence_id = response.json()["data"]["sequence_id"]
                status = self.get_sequence_status(sender_starkkey, sequence_id)
                if status == 0:
                    time.sleep(1)
                    continue
                assert status == 1
                return sequence_id
            except Exception as e:
                print("Transfer failed", e)
                return False
    
    def get_sequence_status(self, stark_key, sequence_id):
        uri = '/v1/record' + '?sequence_id=' + str(sequence_id) + '&stark_key=' + str(stark_key)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers)
        return r.json()['data'][0]['status']

    def withdrawNFT(self, stark_private_key, sender_starkkey, receiver, token_type, contract, tokenID, expiration_timestamp=4194303):
        quantum = 1
        asset_id =  hex(get_asset_id(token_type, contract, quantum, int(tokenID)))
        vault_id = self.get_vault_id(sender_starkkey, asset_id)
        receiver_vault_id = self.get_vault_id(receiver, asset_id)
        nonce = self.get_nonce(sender_starkkey)
        data = {}
        data['asset_id'] = str(asset_id)
        data['receiver_vault_id'] = str(receiver_vault_id)
        data['sender_vault_id'] = str(vault_id)
        data['nonce'] = str(nonce)
        data['sender_private_key'] = str(stark_private_key)
        data['amount'] = "1"
        data['receiver'] = str(receiver)
        data['expiration_timestamp'] = str(expiration_timestamp)
        data['stark_key'] = str(sender_starkkey)

        transfer_data = get_transfer_data(data)

        url = self.endpoint + '/v1/withdrawalto'
        headers = {'Content-Type': 'application/json'}
        while True:
            try:
                response = request(url, transfer_data, headers)
                sequence_id = response.json()["data"]["sequence_id"]
                status = self.get_sequence_status(sender_starkkey, sequence_id)
                if status == 0:
                    time.sleep(1)
                    continue
                assert status == 1
                return sequence_id
            except Exception as e:
                print("Transfer failed", e)
                return False
            
    def mintNFT(self, api_key, contract_address, stark_key, amount):
        uri = '/v1/mints'
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json', "X-API-KEY": api_key}
        data = {}
        data['contract_address'] = str(contract_address)
        data['stark_key'] = str(stark_key)
        data['amount'] = str(amount)
        r = requests.post(url, headers = headers, json = data)
        return r.json()['data']['sequence_ids']

def get_transfer_data(data):
    r, s = get_signature_local(data)
    original_transfer_data = {}
    original_transfer_data['amount'] = data['amount']
    original_transfer_data['nonce'] = int(data['nonce'])
    original_transfer_data['vault_id'] = data['sender_vault_id']
    original_transfer_data['receiver_vault_id'] = data['receiver_vault_id']
    original_transfer_data['stark_key'] = data["stark_key"]
    original_transfer_data['receiver'] = data["receiver"]
    original_transfer_data['signature'] = {"r": r, "s": s}
    original_transfer_data['asset_id'] = data['asset_id']
    original_transfer_data['expiration_timestamp'] = int(data['expiration_timestamp'])
    return original_transfer_data
if __name__ == "__main__":
    obj = Reddio("testnet")
    # print(obj.get_balances("0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a"))

    # print(obj.transferNFT('private_key', '0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a', '0x1ada455b26b246260b7fd876429289639d7a0ce5fe295ff2355bd4f4da55e2', 'ERC721', '0x941661Bd1134DC7cc3D107BF006B8631F6E65Ad5', '618'))
    # print(obj.withdrawNFT('private_key', '0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a', '0xffc882996cFAB2C8B9983394E09bb025a98e52bc', 'ERC721', '0x941661Bd1134DC7cc3D107BF006B8631F6E65Ad5', '663'))
    # print(obj.get_balances("0x1ada455b26b246260b7fd876429289639d7a0ce5fe295ff2355bd4f4da55e2"))