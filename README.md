# red-py-sdk

![](https://img.shields.io/pypi/pyversions/Django.svg)


### install

```
pip3 install red-py-sdk
```

### Usage

#### Import

```
from redpysdk import Reddio
```

#### Init object
Init the object, you can use 'testnet' or 'mainnet' to init the sdk
```
reddio = Reddio("testnet")
```

#### Get StarkKey Pair
##### Usage
```
get_stark_key_pair()
```
It will generate an random starkkey pair

##### Example
```
>>> reddio.get_stark_key_pair()
('0x395d1708ab0ee91efcb7f26a2f4fcbe20faf3c7390517667fed37b0e481882a', '0x5aa1b67a486b6564a2b6ae7426950c03dfe6991f9d34ea45b6b0be0672a1818')
```




#### Get Balance

##### Usage

```
get_balances(stark_key, page=1, limit=10)
```
It will return the starkkey's balance. including ERC20/ETH/ERC721

##### Example

```
reddio.get_balances("0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a")
```




#### Transfer

##### Usage
```
transferNFT(stark_private_key, starkkey, receiver, token_type, contract, tokenID, expiration_timestamp=4194303)
```

parameters
- stark_private_key: The private key of layer2
- starkkey: The stark key of layer2
- receiver: The receiver, should be starkkey of other account
- token_type: ERC721 or ERC721M. if mint on layer2 then it should be ERC721M. else it should be ERC721
- tokenID: The token id
- expiration_timestamp: When will it expiration, it is unix timestamp/3600

##### Example

```
reddio.transferNFT('private_key', '0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a', '0x1ada455b26b246260b7fd876429289639d7a0ce5fe295ff2355bd4f4da55e2', 'ERC721', '0x941661Bd1134DC7cc3D107BF006B8631F6E65Ad5', '618'))
```

In the example, you should replace the 'private_key' to the private key of the starkkey




#### Withdrawal

##### Usage
```
withdrawNFT(stark_private_key, starkkey, receiver, token_type, contract, tokenID, expiration_timestamp=4194303)
```

parameters
- stark_private_key: the private key of layer2
- starkkey: the stark key of layer2
- receiver: the receiver, should be starkkey of other account
- token_type: ERC721 or ERC721M. if mint on layer2 then it should be ERC721M. else it should be ERC721
- tokenID: the token id
- expiration_timestamp: when will it expiration, it is unix timestamp/3600

##### Example

```
reddio.withdrawNFT('private_key', '0x6ecaebbe5b9486472d964217e5470380782823bb0d865240ba916d01636310a', '0xffc882996cFAB2C8B9983394E09bb025a98e52bc', 'ERC721', '0x941661Bd1134DC7cc3D107BF006B8631F6E65Ad5', '663')
```

In the example, you should replace the 'private_key' to the private key of the starkkey






