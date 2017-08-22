import requests,time
import json
from bs4 import BeautifulSoup as bs
import threadpool
import queue
import threading

proxy=set()

def xunproxy():
    #讯代理爬取
    headers={
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36",
        "Host":"www.xdaili.cn"
    }
    url="http://www.xdaili.cn/ipagent//freeip/getFreeIps?page=1&rows=10"
    resp=requests.get(url=url,headers=headers)
    resp.encoding='utf-8'
    data=(json.loads(resp.text))["RESULT"]
    proxy=set()
    for j in data["rows"]:
        proxy.add(j["ip"]+":"+j["port"])

#快代理
def kuaidaili(que,lock):
    url=""
    if not que.empty():
        url=que.get()
    time.sleep(1)
    headers={}
    headers["User-Agent"]="Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36"
    headers["Host"]="www.kuaidaili.com"
    headers["Referer"]="http://www.kuaidaili.com/"
    resp=requests.get(url=url,headers=headers)
    resp.encoding="utf-8"
    if resp.status_code==200:
        soup=bs(resp.text,"lxml")
        tbody=soup.find("tbody")
        tr=tbody.find_all("tr")
        for j in tr:
            td=j.find_all("td")
            ipinfo=td[0].get_text()+":"+td[1].get_text()
            try:
                lock.acquire()
                proxy.add(ipinfo)
                lock.release()
            except:
                print("代理添加失败！",i)

proxyok=set()
#验证代理是否OK
def validate(i,lock):
    proxies={"http": "http://"+i}
    testurl="https://www.baidu.com/"
    try:
        resp=requests.get(url=testurl,proxies=proxies,timeout=3)
        if resp.status_code==200:
            print("该代理存活",i)
            try:
                lock.acquire()
                proxyok.add(i)
                lock.release()
            except:
                print("代理添加失败！",i)
        else:
            print("该代理失效",i,resp.status_code)
    except:
        print("该代理失效",i)

que = queue.Queue()
pool = threadpool.ThreadPool(20)
#向队列中添加
for i in range(1,15):
    que.put("http://www.kuaidaili.com/free/inha/"+str(i)+"/")
lock=threading.Lock()
xunproxy()

requestss=threadpool.makeRequests(kuaidaili,((que.get()),(lock)))
[pool.putRequest(req) for req in requestss]
# for i in proxy:
#     requestss=threadpool.makeRequests(validate,([i,lock]))
#     [pool.putRequest(req) for req in requestss]

pool.wait()
print(proxyok)

