import requests
import logging
import time
import math

from .settings import REDDIO_ENDPOINT_TESTNET, REDDIO_ENDPOINT_MAINNET

from .http_utils import request
from .starkex_utils import get_signature_local,get_order_with_fee_signature_local, get_asset_id
from .signature import get_random_private_key,private_to_stark_key,pedersen_hash,sign

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
        try:
            return r.json()['data']['vault_ids'][0]
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e
    
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
        try:
            return r.json()['data']
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e


    def get_balances(self, stark_key, page=1, limit=10):
        uri = '/v1/balances' + '?stark_key=' + str(stark_key) + '&page=' + str(page) + '&limit=' + str(limit)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json', "User-Agent":"ReddioFrame"}
        r = requests.get(url, headers = headers)
        try:
            return r.json()["data"]["list"]
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e

    def get_balances_v2(self, stark_key):
        uri = '/v2/balances' + '?stark_key=' + str(stark_key)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json', "User-Agent":"ReddioFrame"}
        r = requests.get(url, headers = headers)
        try:
            return r.json()["data"]
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e


    def get_orders(self, contract_address, token_ids=None,direction=0):
        uri = '/v1/orders' + '?contract_address=' + str(contract_address)
        if isinstance(token_ids, list):
            token_ids = ','.join(str(i) for i in token_ids)
            uri += '&token_ids=' + str(token_ids)
        url = self.endpoint + uri
        if direction == 1:
            url += '&direction=1'
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers)
        order_list = []
        try:
            for order in r.json()["data"]["list"]:
                if order["stark_key"] != "":
                    order_list.append(order)
            return order_list
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e

    def get_collection(self, contract_address, token_ids=None):
        uri = '/v1/collection' + '?quote_contract_address=' + str(contract_address)
        if isinstance(token_ids, list):
            token_ids = ','.join(str(i) for i in token_ids)
            uri += '&token_ids=' + str(token_ids)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers)
        order_list = []
        try:
            return r.json()["data"]["list"]
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e

    def list_nft_by_user(self, stark_key, contract_address):
        uri = '/v1/balances' + '?stark_key=' + str(stark_key) + '&contract_address=' + str(contract_address) + '&limit=1000'
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers)
        try:
            return r.json()["data"]["list"]
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e

    def list_user_nfts(self, stark_key, contract_address):
        nfts = self.list_nft_by_user(stark_key, contract_address)
        nft_list = []
        for nft in nfts:
            if nft["balance_available"] > 0 and int(nft["token_id"]) > 668:
                nft_list.append(nft)
        return nft_list
    
    def list_token_ids(self, stark_key, contract_address):
        token_infos = self.list_nft_by_user(stark_key, contract_address)
        token_list = []
        for token_info in token_infos:
            if token_info["balance_available"] > 0:
                token_list.append(token_info["token_id"])
        return token_list

    def get_nonce(self, stark_key):
        """
        Gets the nonce for a given stark key.
        """
        data = {"stark_key": stark_key}
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url = '%s/v1/nonce' % self.endpoint , params = data, headers = headers)
        try:
            return r.json()['data']['nonce']
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e
    
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
        r = request(url, transfer_data, headers)
        try:
            return r.json()
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e
    
    def get_contract_info(self, contract_address):
        uri = '/v1/contract_info' + '?contract_address=' + str(contract_address)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers)
        try:
            return r.json()['data']
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e
    
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
                raise e
    
    def get_sequence(self, stark_key, sequence_id):
        uri = '/v1/record' + '?sequence_id=' + str(sequence_id) + '&stark_key=' + str(stark_key)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers)
        try:
            return r.json()['data'][0]
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e
    
    def get_sequence_status(self, stark_key, sequence_id):
        uri = '/v1/record' + '?sequence_id=' + str(sequence_id) + '&stark_key=' + str(stark_key)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json'}
        r = requests.get(url, headers = headers)
        try:
            return r.json()['data'][0]['status']
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e
            
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
                raise e
            
    def mintNFT(self, api_key, contract_address, stark_key, amount):
        uri = '/v1/mints'
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json', "X-API-KEY": api_key}
        data = {}
        data['contract_address'] = str(contract_address)
        data['stark_key'] = str(stark_key)
        data['amount'] = str(amount)
        r = requests.post(url, headers = headers, json = data)
        try:
            return r.json()['data']['sequence_ids']
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e


    def get_order_info(self, stark_key, contract1Type, contract1Address, contract1TokenID, contract2Type, contract2Address, contract2TokenID):
        uri = '/v1/order/info' + '?stark_key=' + str(stark_key) + '&contract1=' + str(contract1Type) + ':' + str(contract1Address) + ':' + str(contract1TokenID) + '&contract2=' + str(contract2Type) + ':' + str(contract2Address) + ':' + str(contract2TokenID)
        url = self.endpoint + uri
        headers = {'Content-Type': 'application/json', "User-Agent":"ReddioFrame"}
        r = requests.get(url, headers = headers)
        try:
            return r.json()['data']
        except (TypeError, KeyError):
            return r.json()['error']
        except Exception as e:
            raise e   
    
    def sell_nft(self, contract_type, contract_address, tokenID, price,  stark_private_key,base_token_type = "ETH", base_token_contract="eth", marketplace_uuid = ""):
        quantum = 1
        amount = 1
        expiration_timestamp = 4194303
        asset_id = hex(get_asset_id(contract_type, contract_address, quantum, int(tokenID)))
        quote_token = asset_id
        direction = 0
        token_sell = quote_token
        account_id = self.get_stark_key_by_private_key(stark_private_key)
        order_info = self.get_order_info(account_id, base_token_type,base_token_contract,"1",contract_type,contract_address,tokenID)
        base_token = order_info['base_token']
        token_buy = base_token
        vault_id_buy = order_info["vault_ids"][0]
        vault_id_sell = order_info["vault_ids"][1]
        nonce = order_info["nonce"]
        price = int(int(price * 10**order_info["contracts"][0]["decimals"])/order_info["contracts"][0]["quantum"])

        fee_limit = int(math.ceil(price * float(order_info["fee_rate"])))

        data = {
            "sender_private_key": stark_private_key,
            "amount_buy":str(price),
            "amount_sell":str(amount),
            "token_buy":str(token_buy),
            "token_sell":str(token_sell),
            "vault_id_buy":str(vault_id_buy),
            "vault_id_sell":str(vault_id_sell),
            "expiration_timestamp":expiration_timestamp,
            "nonce":nonce,
            "fee_limit":str(fee_limit),
            "fee_token":str(token_buy),
            "fee_vault_id":str(vault_id_buy)
        }

        r,s = get_order_with_fee_signature_local(data)
        fee_info = {
            "fee_limit":fee_limit,
            "token_id": base_token,
            "source_vault_id":int(vault_id_buy),
        }
        order = {
            "amount": str(amount),
            "price": str(price),
            "stark_key": str(account_id),
            "amount_buy": str(amount * price),
            "amount_sell": str(amount),
            "token_buy": str(token_buy),
            "token_sell": str(token_sell),
            "vault_id_buy": str(vault_id_buy),
            "vault_id_sell": str(vault_id_sell),
            "expiration_timestamp": expiration_timestamp,
            "base_token": str(base_token),
            "quote_token": str(quote_token),
            "nonce": nonce,
            "signature": {
                "r": r,
                "s": s
            },
            "fee_info": fee_info,
            "direction": direction,
            "marketplace_uuid": marketplace_uuid,
        }

        data = order
        headers = {'Content-Type': 'application/json', "User-Agent":"ReddioFrame"}
        url = self.endpoint + '/v1/order'
        resp = request(url, data, headers)
        if resp.json()["status"] == "OK":
            return resp.json()["data"]["sequence_id"]
        return resp.json()["error"]

    def buy_nft(self, contract_type, contract_address, tokenID, price, stark_private_key, base_token_type = "ETH", base_token_contract="eth", marketplace_uuid = ""):
        quantum = 1
        asset_id = hex(get_asset_id(contract_type, contract_address, quantum, tokenID))
        amount = 1
        quote_token = asset_id
        direction = 1

        account_id = self.get_stark_key_by_private_key(stark_private_key)

        token_buy = quote_token

        order_info = self.get_order_info(account_id, base_token_type,base_token_contract,"1",contract_type,contract_address,tokenID)

        base_token = order_info['base_token']
        token_sell = base_token
        vault_id_sell = order_info["vault_ids"][0]
        vault_id_buy = order_info["vault_ids"][1]
        nonce = order_info["nonce"]

        price = int(int(price * 10**order_info["contracts"][0]["decimals"])/order_info["contracts"][0]["quantum"])

        fee_limit = int(math.ceil(price * float(order_info["fee_rate"])))


        expiration_timestamp = 4194303

        data = {
            "sender_private_key": stark_private_key,
            "amount_buy":"1",
            "amount_sell":str(amount*price),
            "token_buy":str(token_buy),
            "token_sell":str(token_sell),
            "vault_id_buy":str(vault_id_buy),
            "vault_id_sell":str(vault_id_sell),
            "expiration_timestamp":expiration_timestamp,
            "nonce":nonce,
            "fee_limit":"1",
            "fee_token":str(base_token),
            "fee_vault_id":str(vault_id_sell)
        }
        r,s = get_order_with_fee_signature_local(data)
        fee_info = {
            "fee_limit":1,
            "token_id": base_token,
            "source_vault_id":int(vault_id_sell),
        }
        order = {
            "amount": str(amount),
            "price": str(price),
            "stark_key": str(account_id),
            "amount_buy": str(1),
            "amount_sell": str(amount * price),
            "token_buy": str(token_buy),
            "token_sell": str(token_sell),
            "vault_id_buy": str(vault_id_buy),
            "vault_id_sell": str(vault_id_sell),
            "expiration_timestamp": expiration_timestamp,
            "base_token": str(base_token),
            "quote_token": str(quote_token),
            "nonce": nonce,
            "signature": {
                "r": r,
                "s": s
            },
            "fee_info": fee_info,
            "direction": direction
        }

        data = order
        headers = {'Content-Type': 'application/json', "User-Agent":"ReddioFrame"}
        url = self.endpoint + '/v1/order'
        resp = request(url, data, headers)
        if resp.json()["status"] == "OK":
            return resp.json()["data"]["sequence_id"]
        return resp.json()["error"]

    def cancel_order(self, order_id, stark_private_key):
        stark_public_key = self.get_stark_key_by_private_key(stark_private_key)

        r, s = sign_order(order_id, int(stark_private_key,16))
    
        headers = {'Content-Type': 'application/json'}
        url = self.endpoint + '/v1/orders/' + str(order_id) + '/cancel'
        data = {
            "stark_key": stark_public_key,
            "signature": {
                "r": str(r),
                "s": str(s)
            }
        }
        resp = request(url, data, headers)
        if resp.json()["status"] == "OK":
            return resp.json()["data"]["sequence_id"]
        return resp.json()["error"]

def sign_order(order_id, starkPrivateKey):
    msg_hash = pedersen_hash(int(order_id),0)
    r, s = sign(msg_hash, starkPrivateKey)
    return hex(r), hex(s)

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