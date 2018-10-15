import pymysql
MYSQL_HOST = 'localhost'
MYSQL_PORT = 3306
MYSQL_PASSWD = 'root5821012'
MYSQL_USERNAME = 'root'
MYSQL_DATABASE = 'pythontest'
import pymysql
class Mysql():
    def __init__(self,host=MYSQL_HOST,username=MYSQL_USERNAME,password=MYSQL_PASSWD,
                 port=MYSQL_PORT,database=MYSQL_DATABASE):
        try:
            self.db=pymysql.connect(host,username,password,database,charset='utf8',port=port)
            self.cursor = self.db.cursor()
        except pymysql.MySQLError as e:
            print(e.args)
    def insert(self,table,data):
        keys= ', '.join(data.keys())
        values = ', '.join(['%s']*len(data))
        sql_query = 'insert into %s(%s) VALUES (%s)'%(table,keys,values)
        try:
            self.cursor.execute(sql_query,tuple(data.values()))
            self.db.commit()
        except pymysql.MySQLError as e:
            print(e.args)
            self.db.rollback()

