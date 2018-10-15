import sys
sys.path.append('D:\pythonsoft\\anaconda\\anzhuang\Lib\site-packages')
sys.path.append('D:\pythonsoft\\anaconda\\anzhuang\Scripts')

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote
brower = webdriver.Chrome()
wait = WebDriverWait(brower,10)
KeyWord = 'ipad'
def index_page(page):
    '''
    抓取索引页
    :param page:页码
    :return:
    '''
    print("正在抓取第",page,'页')
    try:
        url = 'https://s.taobao.com/search?q='+quote(KeyWord)
        brower.get(url)
        if page>1:
            input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager div.form>input')))
            submit = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,'#mainsrp-pager div.form>span.btn.J_Submit')))
            input.clear()
            input.send_keys(page)
            submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR,'#mainsrp-pager li.item.active>span'),str(page)))
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'.m-itemlist .items .item')))
        get_products()
    except TimeoutException:
        index_page(page)
from pyquery import PyQuery as pq
def get_products():
    '''
    提取商品信息
    :return:
    '''
    html = brower.page_source
    doc = pq(html)
    items = doc('.m-itemlist .items .item').items()
    for item in items:
        product = {
            'pictures':item.find('.pic .img').attr('data-src'),
            'price':item.find('.price').text(),
            'deal':item.find('.deal-cnt').text(),
            'title':item.find('.title').text(),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        print(product)
        save_page(product)
import pymongo
MONGGO_URL = 'localhost'
MONGGO_DB = 'taobao'
MONGO_COLLECTION = 'products'
client = pymongo.MongoClient(MONGGO_URL)
db = client[MONGGO_DB]
def save_page(product):
    '''
    保存抓取的产品信息
    :param product: 产品字典信息
    :return:
    '''
    try:
        if db[MONGO_COLLECTION].insert(product):
            print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')
def main():
    index_page(1)
if __name__ == '__main__':
    main()
