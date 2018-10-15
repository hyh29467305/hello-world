import sys
sys.path.append('D:\pythonsoft\\anaconda\\anzhuang\Lib\site-packages')
import requests
import urllib3
import re
import json
import time
def get_one_page(url):
    headers = {
        'User-Agent': 'Mozilla / 5.0(WindowsNT10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko)'
                      ' Chrome / 67.0.3396.79Safari / 537.36'
    }
    responst = requests.get(url,headers=headers)
    if responst.status_code == 200:
        return responst.text
def parse_page(html):
    pattern = re.compile('<dd>.*?board-index.*?>(\d+)</i>.*?<img.*?alt.*?src="(.*?)".*?</a>.*?name">'
                         +'<a.*?>(.*?)</a>.*?star">(.*?)</p>.*?releasetime">(.*?)</p>.*?integer">'
                         +'(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',re.S)
    items = re.findall(pattern,html)
    for item in items:
        yield {
            'index':item[0],
            'image':item[1],
            'title':item[2].strip(),
            'stars':item[3].strip()[3:] if len(item[3]) > 3 else "" ,
            'releasetime':item[4].strip()[5:] if len(item[4])>5 else "",
            'score':item[5].strip()+item[6].strip()
        }
def save_page(item):
    with open('maoyan.txt','a',encoding='utf-8') as f:
        f.write(json.dumps(item,ensure_ascii=False) + '\n')
def main(offset):
    url = 'http://maoyan.com/board/4?offset='
    url += str(offset)
    html = get_one_page(url)
    for item in parse_page(html):
        print(item)
        save_page(item)
if __name__ == '__main__':
    for i in range(10):
        main(i*10)
        time.sleep(1)