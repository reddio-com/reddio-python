import requests

def request(url, data, headers=None):
    return requests.post(url, json=data, headers=headers)