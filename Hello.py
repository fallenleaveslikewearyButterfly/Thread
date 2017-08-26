import requests, time,json,queue,threading,re
from bs4 import BeautifulSoup as bs
from concurrent.futures import ThreadPoolExecutor

class proxycrawler():
    def __init__(self):
        self.producepool=ThreadPoolExecutor(max_workers=20)
        #验证队列
        self.consumerpool=ThreadPoolExecutor(max_workers=20)
        self.proxy=queue.Queue()
        self.proxyok=set()
        self.lock=threading.Lock()

    def xunproxy(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
            "Host": "www.xdaili.cn"
        }
        url = "http://www.xdaili.cn/ipagent//freeip/getFreeIps?page=1&rows=10"
        resp = requests.get(url=url, headers=headers)
        resp.encoding = 'utf-8'
        data = (json.loads(resp.text))["RESULT"]
        proxy = set()
        for j in data["rows"]:
            self.proxy.put(j["ip"] + ":" + j["port"])

    def kuaiproxy(self,urls):
        headers = {}
        headers[
            "User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"
        headers["Host"] = "www.kuaidaili.com"
        headers["Referer"] = "http://www.kuaidaili.com/"
        while not urls.empty():
            url = urls.get()
            resp = requests.get(url=url, headers=headers)
            resp.encoding = "utf-8"
            for i in range(0, 3):
                if resp.status_code == 503:
                    time.sleep(5)
                    resp = requests.get(url=url, headers=headers)
            #print(resp.status_code, url)
            if resp.status_code == 200:
                soup = bs(resp.text, "lxml")
                tbody = soup.find("tbody")
                tr = tbody.find_all("tr")
                for j in tr:
                    td = j.find_all("td")
                    ipinfo = td[0].get_text() + ":" + td[1].get_text()
                    #print("添加代理成功",ipinfo)
                    self.proxy.put(ipinfo)

    def xiciproxy(self,urls):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
            "Host": "www.xicidaili.com"
        }
        while not urls.empty():
            time.sleep(10)
            url = urls.get()
            resp = requests.get(url=url, headers=headers)
            resp.encoding = 'utf-8'
            if resp.status_code==200:
                soup = bs(resp.text, "lxml")
                tr = soup.find_all("tr", class_=re.compile(".*"))
                for j in tr:
                    td = j.find_all("td")
                    if td is not None:
                        ipinfo = td[1].get_text() + ":" + td[2].get_text()
                        self.proxy.put(ipinfo)
            else:
                print(resp.status_code,url)

    def validate(self):
        while not self.proxy.empty():
            i = self.proxy.get()
            proxies = {"http": "http://" + i}
            testurl = "http://tieba.baidu.com/f?kw=%BD%AD%BA%BA%B4%F3%D1%A7&fr=ala0&tpl=5"
            try:
                resp = requests.get(url=testurl, proxies=proxies, timeout=3)
                if resp.status_code == 200:
                    try:
                        self.lock.acquire()
                        self.proxyok.add(i)
                        #print("该代理存活,添加成功！", i, threading.current_thread().getName())
                        self.lock.release()
                    except:
                        print("代理添加失败！", i, threading.current_thread().getName())
                else:
                    pass
                    #print("该代理失效", i, resp.status_code, threading.current_thread().getName())
            except:
                pass
                #print("该代理失效", i, threading.current_thread().getName())

    def waitresult(self,futures):
        for future in futures:
            while not future.done():
                pass

    def dispath(self):
        urlskuaidaili=queue.Queue()
        for i in range(1,16):
            urlskuaidaili.put("http://www.kuaidaili.com/free/inha/" + str(i) + "/")
        #开启三个线程抓代理
        self.producepool.submit(self.xunproxy,)
        futures={self.producepool.submit(self.kuaiproxy, urlskuaidaili): x for x in range(0,3)}
        self.waitresult(futures)

        urlxici = queue.Queue()
        for i in range(1, 10):
            urlxici.put("http://www.xicidaili.com/nn/" + str(i))
        # 开启三个线程抓西祠代理
        futures = {self.producepool.submit(self.xiciproxy, urlxici): x for x in range(0, 3)}
        self.waitresult(futures)

        print(self.proxy.qsize())
        futuresval={self.consumerpool.submit(self.validate,):x for x in range(0,20)}
        self.waitresult(futuresval)
        return self.proxyok

craw=proxycrawler()
proxyok=craw.dispath()
print([i for i in proxyok])
