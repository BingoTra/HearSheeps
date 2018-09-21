import time
from queue import Queue
from threading import Thread
import requests


class DownloadDecorator:
    def __init__(self, session):

        self.mas = []
        self.s = session

    def __call__(self, url, seters, destination, *args):
        self.mas.append([url, seters, destination, args])

    def download(self):
        print('Downloading')
        queue = Queue()
        ti = time.time()
        num_worker_threads = 11
        masImage = []

        for item in self.mas:
            queue.put(item)

        def do_work(item):
            # Выполняем запросы
            try:
                print(item)
                r = self.s.get(item[0], proxies=self.s.proxies)
                masImage.append([r, item[1], item[2], item[3]])
            except:
                print('Ошибка загрузки фото')
                pass

        def worker():
            while True:
                # Получаем задание из очереди
                if queue.qsize() != 0:
                    url = queue.get()
                    # Выполняем запросы
                    do_work(url)
                    # Сообщаем о выполненном задании
                    queue.task_done()
                else:
                    break

        # Создаем и запускаем потоки, которые будут обслуживать очередь
        for i in range(num_worker_threads):
            t = Thread(target=worker)
            t.setDaemon(True)
            t.start()

        # Ставим блокировку до тех пор пока не будут выполнены все задания
        queue.join()
        print('downloaded time:', time.time() - ti)
        self.mas.clear()

        return masImage
