from db import RedisClient
from flask import Flask,g
__all__ = ['app']
app = Flask(__name__)
def get_conn():
    if not hasattr(g,'redis'):
        g.redis = RedisClient()
    return g.redis
@app.route('/')
def index():
    return "<h2>Welcome to Proxy System Pool</h2>"
@app.route('/random')
def get_proxy():
    conn = get_conn()
    return conn.random()
@app.route('/count')
def get_count():
    '''
    获得代理的数量
    :return:
    '''
    conn = get_conn()
    return str(conn.count())
if __name__ == '__main__':
    app.run(port=8080)