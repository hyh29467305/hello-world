import sys
sys.path.append('D:\pythonsoft\\anaconda\\anzhuang\Lib\site-packages')
sys.path.append('D:\pythonsoft\\anaconda\\anzhuang\Scripts')
from urllib import parse
from urllib.request import ProxyHandler,build_opener,urlopen
import urllib.request
from urllib import error
import json
proxy = ProxyHandler({
    'http':'120.194.18.90:81'
})
opener = build_opener(proxy)
url = 'http://www.baidu.com'
urllib.request.install_opener(opener)
try:
    response = urlopen(url)
    print(response.read().decode('utf-8'))
except error.URLError as e:
    print(e.reason)