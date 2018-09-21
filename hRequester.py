import time
from queue import Queue
from threading import Thread
import requests
from multiprocessing.dummy import Pool as ThreadPool

class Requccester:
    def __init__(self):

        self.mas = []

    def __call__(self, url, session, *args):
        self.mas.append([url, session, args])

    def fillPost(self, url, dic, session, *args):
        self.mas.append([url, dic, session, args])

    def hFillPost(self, url, session, *args, **kwargs):
        self.mas.append([url, session, args, kwargs])

    def request(self):
        print('Requesting')
        mainQueue = Queue()
        timeoutQueue = Queue()
        ti = time.time()
        num_worker_threads = 5
        masData = []

        for item in self.mas:
            mainQueue.put(item)

        def do_work(item):
            # Выполняем запросы
            try:
                session = item[1]
                print('Поток')
                r = session.get(item[0], proxies=item[1].proxies, timeout=15)
                masData.append([r, item[1], item[2]])
                return
            except requests.exceptions.ProxyError:
                print('Proxy Error', item[1].proxies)
            except requests.exceptions.Timeout:
                print('Таймайут', item[1].proxies)
                mainQueue.put(item)
                return


        def worker(queue):
            while True:
                url = queue.get()
                do_work(url)
                queue.task_done()

        for i in range(num_worker_threads):
            t = Thread(target=worker, args=(mainQueue,))
            t.setDaemon(True)
            t.start()

        mainQueue.join()

        print('requested time:', time.time() - ti)
        self.mas.clear()

        return masData

    def postRequest(self):
        print('Post requesting')
        queue = Queue()
        ti = time.time()
        num_worker_threads = 5
        masData = []

        for item in self.mas:
            queue.put(item)

        def do_work(item):
            # Выполняем
            print('Поток')
            try:
                session = item[2]
                r = session.post(item[0], files=item[1], proxies=item[2].proxies)
                masData.append([r, item[2], item[3]])
            except requests.exceptions.ProxyError:
                print('Proxy Error', item[1].proxies)
            except requests.exceptions.Timeout:
                print('Таймайут', item[1].proxies)
                queue.put(item)

        def worker():
            while True:
                url = queue.get()
                do_work(url)
                queue.task_done()

        # Создаем и запускаем потоки, которые будут обслуживать очередь
        for i in range(num_worker_threads):
            t = Thread(target=worker)
            t.setDaemon(True)
            t.start()

        # Ставим блокировку до тех пор пока не будут выполнены все задания
        queue.join()
        print('post requested time:', time.time() - ti)
        self.mas.clear()

        return masData

    def hPostRequest(self):
        print('HPost requesting')
        mainQueue = Queue()
        timeoutQueue = Queue()
        ti = time.time()
        num_worker_threads = 8
        masData = []

        for item in self.mas:
            mainQueue.put(item)

        def do_work(item):
            # Выполняем запросы
            session = item[1]
            try:
                r = session.post(item[0], proxies=session.proxies, **item[3], timeout=10)
                masData.append([r, item[1], item[2], item[3]])
                return
            except requests.exceptions.ProxyError:
                print('Proxy Error', item[1].proxies)
            except requests.exceptions.Timeout:
                print('Таймайут', item[1].proxies)
                timeoutQueue.put(item)
                return


        def worker(queue):
            while True:
                url = queue.get()
                do_work(url)
                queue.task_done()

        for i in range(num_worker_threads):
            t = Thread(target=worker, args=(mainQueue,))
            t.setDaemon(True)
            t.start()

        mainQueue.join()

        for i in range(num_worker_threads):
            t = Thread(target=worker, args=(timeoutQueue,))
            t.setDaemon(True)
            t.start()

        timeoutQueue.join()

        print('post requested time:', time.time() - ti)
        self.mas.clear()

        return masData

class HRequester:
    def __init__(self):
        self.taskList = []

    def __call__(self, url, session, *args, **kwargs):
        self.taskList.append([url, session, args, kwargs])

    def do_work(self, item):
        # Выполняем запросы
        try:
            #time.sleep(1)
            print('Поток')
            url, session, args, kwargs = item
            r = session.get(url, proxies=session.proxies, **kwargs, timeout=10)
            session.close()
            return [r, session, args]
        except requests.exceptions.ProxyError as e:
            print(repr(e))
            return self.do_work(item)
        except requests.exceptions.Timeout as e:
            print('Timeout', e)
            return self.do_work(item)
        except requests.exceptions.ConnectionError as e:
            print(e)

    def request(self):
        print('Requesting')
        ti = time.time()
        pool = ThreadPool(50)

        results = pool.map(self.do_work, self.taskList)

        pool.close()
        pool.join()

        lenList = len(results)
        i = 0

        while i < lenList:

            if not results[i]:
                results.pop(i)
                lenList -= 1

            else:
                i += 1


        print('requested time:', time.time() - ti)
        self.taskList.clear()

        return results


class HPostRequester:
    def __init__(self):

        self.taskList = []

    def __call__(self, url, session, *args, **kwargs):
        self.taskList.append([url, session, args, kwargs])

    def do_work(self, item):

        try:
            url, session, args, kwargs = item
            print('Поток')
            r = session.post(url, proxies=session.proxies, **kwargs, timeout=10)
            return [r, session, args]
        except requests.exceptions.ProxyError as e:
            print(repr(e))
            return self.do_work(item)
        except requests.exceptions.Timeout as e:
            print('Timeout', e)
            return self.do_work(item)
        except requests.exceptions.ConnectionError as e:
            print(e)


    def request(self):
        print('Post requesting')
        ti = time.time()
        pool = ThreadPool(50)

        results = pool.map(self.do_work, self.taskList)

        pool.close()
        pool.join()

        lenList = len(results)
        i = 0

        while i < lenList:

            if not results[i]:
                results.pop(i)
                lenList -= 1

            else:
                i += 1


        print('requested time:', time.time() - ti)
        self.taskList.clear()

        return results