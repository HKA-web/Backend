import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def post_ignore_ssl(url, **kwargs):
    return requests.post(url, verify=False, **kwargs)
