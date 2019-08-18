"""
ALJ 08/18/2019 -> API Documentation: https://www.goodreads.com/api/index
"""

import requests

def api_fetch_goodreads(url_passed, parameters_passed):
    url = url_passed
    querystring = parameters_passed

    headers = {
        'Accept': "*/*",
        'Host': "www.goodreads.com",
        'accept-encoding': "gzip, deflate",
        'Connection': "keep-alive",
        'cache-control': "no-cache"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.text