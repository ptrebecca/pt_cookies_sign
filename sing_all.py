import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import configparser

from requests import post, session
from json import dumps
from re import compile
from time import sleep,strftime,localtime,time
from random import randint,shuffle




class Sign():
    msg_list = []
    def set_sessino(self, domain, cookie):
        self.session = session()
        self.session.headers.update({"Host": domain})
        self.session.headers.update({"Connection": "keep-alive"})
        self.session.headers.update({"Upgrade-Insecure-Requests": "1"})
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Edg/86.0.622.69"})
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"})
        self.session.headers.update({"Sec-Fetch-Site": "same-origin"})
        self.session.headers.update({"Sec-Fetch-Mode": "navigate"})
        self.session.headers.update({"Sec-Fetch-User": "?1"})
        self.session.headers.update({"Sec-Fetch-Dest": "document"})
        # self.session.headers.update({"Referer": "https://{}/index.php".format(domain)})
        self.session.headers.update({"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"})
        self.session.headers.update({"Cookie": cookie})

    def sign(self, http, domain):
        if 'btschool' in domain:
            url = "{}://{}/index.php?action=addbonus".format(http, domain)
        elif 'hdcity' in domain:
            url = "{}://{}/sign".format(http, domain)
        else:
            url = "{}://{}/attendance.php".format(http, domain)
        is_robot = 0
        html = self.session.get(url=url, verify=False)
        try:
            html.encoding = 'utf-8'
            pattern = compile(r'(今天签到.*?力值)')
            match = pattern.search(html.text)
            print("{}:{}:{}".format(domain, match.group(1),'1'))
            begin_time = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
            self.msg_list.append("{} {}:{}".format(begin_time, domain, match.group(1)))
            is_robot = 1
        except:
            pass
        try:
            html.encoding = 'utf-8'
            pattern = compile(r'(\(签到.*?\))')
            match = pattern.search(html.text)
            print("{}:{}:{}".format(domain, match.group(1),'2'))
            begin_time = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
            self.msg_list.append("{} {}:{}".format(begin_time, domain, match.group(1)))
            is_robot = 1
        except:
            pass

        try:
            html = self.session.get(url=url, verify=False)
            html.encoding = 'utf-8'
            if '已经签过' not in html.text:
                # self.msg_list.append("{}:{}".format(domain, '签到失败'))
                pass
            else:
                begin_time = strftime('%Y-%m-%d %H:%M:%S', localtime(time()))
                self.msg_list.append("{} {}:{}".format(begin_time, domain, '签到成功'))
                is_robot = 1
        except:
            pass
        try:
            html.encoding = 'utf-8'
            pattern = compile(r'(\(簽到.*?\))')
            match = pattern.search(html.text)
            print("{}:{}".format(domain, match.group(1)))
            begin_time = strftime('%Y-%m-%d %H:%M:%S',localtime(time()))
            self.msg_list.append("{} {}:{}".format(begin_time, domain, match.group(1)))
            is_robot = 1
        except:
            pass
        if is_robot != 1:
            robot(url)


def get_cookie_ini():
    filename = './cookies/cookies.ini'
    conf = configparser.ConfigParser()
    conf.read(filename)
    sections = conf.sections()
    print(sections)
    domain_list = []

    for i in sections:
        if '' == conf[i]['cookie']:
            pass
        else:
            domain = {}
            domain['domain'] = conf[i]['domain']
            domain['issign'] = conf[i]['issign']
            domain['http'] = conf[i]['http']
            domain['cookie'] = conf[i]['cookie']
            domain_list.append(domain)
    return domain_list


def robot(msg):
    try:
        url = 'https://oapi.dingtalk.com/robot/send?access_token=1330a24b18c7a1fe549fbf142738bfd3585678bd66381b0665104b2cbb7c108d'
        HEADERS = {"Content-Type": "application/json;charset=utf-8"}
        message = 'pt站点签到失败，请在规定时间内登录，否则有封号危险\n{}'.format(msg)
        print(message)
        String_textMsg = {"msgtype": "text", "text": {"content": message}}
        String_textMsg = dumps(String_textMsg)
        res = post(url, data=String_textMsg, headers=HEADERS, verify=False)
    except Exception as e:
        pass

def robot2(msg):
    try:
        url = '钉钉机器人url'
        HEADERS = {"Content-Type": "application/json;charset=utf-8"}
        message = 'pt站点签到情况\n{}'.format(msg)
        print(message)
        String_textMsg = {"msgtype": "text", "text": {"content": message}}
        String_textMsg = dumps(String_textMsg)
        res = post(url, data=String_textMsg, headers=HEADERS, verify=False)
    except Exception as e:
        pass

if __name__ == '__main__':
    domain_list = get_cookie_ini()
    print(domain_list)
    print(len(domain_list))
    sign = Sign()
    shuffle(domain_list)
    for i in domain_list:
        sleep(randint(20, 100))
        sign.set_sessino(domain=i['domain'], cookie=i['cookie'])
        if int(i['issign']) == 1:
            sign.sign(http=i['http'], domain=i['domain'])
        else:
            pass
    msg_list = sign.msg_list
    msg = ''
    for i in msg_list:
        msg += '{}\n'.format(i)
    robot2(msg)