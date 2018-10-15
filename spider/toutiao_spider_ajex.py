import sys
sys.path.append('D:\pythonsoft\\anaconda\\anzhuang\Lib\site-packages')
import requests
from urllib.parse import urlencode
import os
from hashlib import md5
def get_page(offset):
    params = {
        'offset':offset,
        'format':'json',
        'keyword':'街拍',
        'autoload':'true',
        'count':20,
        'cur_tab':1,
        'from':'search_tab',
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None
def parse_page(json):
    if json.get('data'):
        for item in json.get('data'):
                title = item.get('title')
                image_list = item.get('image_list')
                if image_list:
                    for image in image_list:
                        yield{
                            'title': title,
                            'image': image.get('url')
                        }

def save_page(item):
    headers = {
        'user-agent': 'Mozilla / 5.0(Windows NT 10.0;WOW64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 67.0.3396.79Safari / 537.36'
    }
    if not os.path.exists('./source/'+item.get('title')):
        os.makedirs('./source/'+item.get('title'))
    try:
        response = requests.get('http:'+item.get('image'),headers=headers)
        if response.status_code==200:
            file_path = './source/{0}/{1}.{2}'.format(item.get('title'),md5(response.content).hexdigest(),'.jpg')
            if not os.path.exists(file_path):
                with open(file_path,'wb') as f:
                    f.write(response.content)
            else:
                print('image:{0} has already exist'.format(item.get('image')))
    except requests.ConnectionError :
        print('Failed save the image {0}'.format(item.get('image')))
def main(offset):
    json = get_page(offset)
    for item in parse_page(json):
        print(item)
        save_page(item)
from multiprocessing.pool import Pool
if __name__ == '__main__':
    pool = Pool()
    group_start = 0
    group_end = 20
    groups = ([item * 20 for item in range(group_start,group_end)])
    pool.map(main,groups)
    pool.close()
    pool.join()
