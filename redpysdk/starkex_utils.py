from web3 import Web3
import web3

from .signature import private_to_stark_key, sign
from .starkex_message import get_limit_order_msg_with_fee, get_transfer_msg

def get_asset_info(type, address):
    if type.lower() == "eth":
        return '0x8322fff2'
    elif type == 'ERC20':
        return '0xf47261b0' + address[2:].rjust(64, '0')
    elif type == 'ERC721':
        return '0x02571792' + address[2:].rjust(64, '0')
    elif type == 'ERC721M':
        return '0xb8b86672' + address[2:].rjust(64, '0')
    else:
        return None

def get_asset_type(typ, address, quantum):
    asset_info = get_asset_info(typ, address)
    asset_type = int(web3.Web3.solidityKeccak(['bytes','uint256'], [asset_info, quantum]).hex(), 16) & 0x03FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    return asset_type

def get_asset_id(typ, address, quantum, token_id):
    asset_id = get_asset_type(typ, address, quantum)
    if typ == 'ERC721':
        asset_id = int(web3.Web3.solidityKeccak(['string','uint256','uint256'], [ 'NFT:',asset_id, token_id]).hex(), 16) & 0x03FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    elif typ == "ERC721M":
        blobHash = int(web3.Web3.solidityKeccak(['bytes'], [ hex(token_id) ]).hex(),16)
        asset_id = int(web3.Web3.solidityKeccak(['string','uint256','uint256'], [ 'MINTABLE:',asset_id, blobHash]).hex(), 16) & 0x0000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
        asset_id = asset_id | 0x400000000000000000000000000000000000000000000000000000000000000
    return asset_id

def get_public_key(private_key):
    return hex(private_to_stark_key(int(private_key,16)))

def get_order_with_fee_signature_local(data):
    private_key = data["sender_private_key"]
    data = {'vault_sell':int(data["vault_id_sell"],10), 'vault_buy':int(data["vault_id_buy"],10), 'amount_sell':int(data["amount_sell"]), 'amount_buy':int(data["amount_buy"]), 'token_sell':int(data["token_sell"],16), 'token_buy':int(data["token_buy"],16),'nonce': int(data["nonce"]),'expiration_timestamp':int(data["expiration_timestamp"]),'fee_limit':int(data["fee_limit"]),'fee_token':int(data["fee_token"],16),'fee_vault_id':int(data["fee_vault_id"],10)}
    transfer_msg = get_limit_order_msg_with_fee(**data)
    r, s = sign(transfer_msg, int(private_key,16))
    return hex(r), hex(s)

def get_signature_local(data):
    private_key = data["sender_private_key"]
    data = {'amount': int(data["amount"]), 'nonce': int(data["nonce"]),
            'sender_vault_id': int(data["sender_vault_id"]),
            'token': int(data["asset_id"],16),
            'receiver_vault_id': int(data["receiver_vault_id"]),
            'receiver_public_key': int(data["receiver"],16),
            'expiration_timestamp': int(data["expiration_timestamp"])}
    transfer_msg = get_transfer_msg(**data)
    r, s = sign(transfer_msg, int(private_key,16))
    return hex(r), hex(s)

if __name__ == "__main__":
    stark_private_key = 'a7b68cf2ee72b2a0789914daa8ae928aec21b6b0bf020e394833f4c732d99d'
    stark_key = private_to_stark_key(int(stark_private_key,16))
    print(hex(stark_key))