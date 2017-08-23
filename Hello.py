import requests, time
import json
from bs4 import BeautifulSoup as bs
import queue
import threading
from concurrent.futures import ThreadPoolExecutor

proxy = set()


def xunproxy():
    # 讯代理爬取
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
        proxy.add(j["ip"] + ":" + j["port"])


# 快代理
def kuaidaili(que, lock):
    while not que.empty():
        url=que.get()
        time.sleep(5)
        headers = {}
        headers[
            "User-Agent"] = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"
        headers["Host"] = "www.kuaidaili.com"
        headers["Referer"] = "http://www.kuaidaili.com/"
        resp = requests.get(url=url, headers=headers)
        resp.encoding = "utf-8"
        if resp.status_code == 200:
            soup = bs(resp.text, "lxml")
            tbody = soup.find("tbody")
            tr = tbody.find_all("tr")
            print(que.qsize(),len(tr),url)
            for j in tr:
                td = j.find_all("td")
                ipinfo = td[0].get_text() + ":" + td[1].get_text()
                try:
                    lock.acquire()
                    proxy.add(ipinfo)
                    print("添加代理成功", ipinfo, threading.current_thread().getName())
                    lock.release()
                except:
                    print("代理添加失败！", i, threading.current_thread().getName())


proxyok = set()

# 验证代理是否OK
def validate(proxy, lock):
    while len(proxy)!=0:
        lock.acquire()
        i=proxy.pop()
        lock.release()
        proxies = {"http": "http://" + i}
        testurl = "http://tieba.baidu.com/f?kw=%BD%AD%BA%BA%B4%F3%D1%A7&fr=ala0&tpl=5"
        try:
            resp = requests.get(url=testurl, proxies=proxies, timeout=3)
            if resp.status_code == 200:
                try:
                    lock.acquire()
                    proxyok.add(i)
                    print("该代理存活,添加成功！", i, threading.current_thread().getName())
                    lock.release()
                except:
                    print("代理添加失败！", i,threading.current_thread().getName())
            else:
                print("该代理失效", i, resp.status_code,threading.current_thread().getName())
        except:
            print("该代理失效", i,threading.current_thread().getName())


que = queue.Queue()
# 向队列中添加
for i in range(1, 16):
    que.put("http://www.kuaidaili.com/free/inha/" + str(i) + "/")
lock = threading.Lock()
#xunproxy()
pool = ThreadPoolExecutor(max_workers=20)
task1 = pool.submit(kuaidaili, *(que, lock))
task2 = pool.submit(kuaidaili, *(que, lock))
task3 = pool.submit(kuaidaili, *(que, lock))

while not (task1.done() and task2.done() and task3.done()):
    pass

print(len(proxy),"所有抓取线程都已经执行完毕")

val1=pool.submit(validate,*(proxy,lock))
val2=pool.submit(validate,*(proxy,lock))
val3=pool.submit(validate,*(proxy,lock))
val4=pool.submit(validate,*(proxy,lock))
val5=pool.submit(validate,*(proxy,lock))

while not (val1.done() and val2.done() and val3.done()and val4.done()and val5.done()):
    pass
print(len(proxyok),"所有线程都已经执行完毕")
print(proxyok)

