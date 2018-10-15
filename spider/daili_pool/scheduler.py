TEST_CYCLE = 20
GETER_CYCLE = 20
TESTER_ENABLE = True
GETTER_ENABLE = True
API_ENABLE = True
from tester import Tester
from getter import Getter
from api import app
from multiprocessing import Process
import time
class Scheduler():
    def schedule_tester(self,cycle=TEST_CYCLE):
        tester = Tester()
        while True:
            print("测试代理开始运行")
            tester.run()
            time.sleep(cycle)
    def schecule_getter(self,cycle=GETER_CYCLE):
        getter = Getter()
        while True:
            print("获取代理开始运行")
            getter.run()
            time.sleep(cycle)
    def schedule_api(self):
        app.run()
    def run(self):
        print("代理池开始运行")
        if GETTER_ENABLE:
            getter_process = Process(target=self.schecule_getter)
            getter_process.start()
        if TESTER_ENABLE:
            tester_process = Process(target=self.schedule_tester())
            tester_process.start()
        if API_ENABLE:
            api_process = Process(target=self.schedule_api)
            api_process.start()

if __name__ == '__main__':
    sche = Scheduler()
    sche.run()
