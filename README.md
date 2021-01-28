### 使用方法  `python3 main.py + 配置好的文件` 
    python3 main.py Verify.json
    python3 main.py NoVerify.json
#### 以上分别对应有验证码的demo和无验证码的demo

--- 
#### Tips:
    你可以以域名作为配置文件名字加载：python3 main.py qq.com.json
    当然你也可以在开启上面任务同时开启：  python3 main.py baidu.com.json
    这样就是利用多进程啦！！！
### 首次安装依赖
    pip3 install gevent requests
---
## 配置说明
    1. speed 是调节速度的，适当调节没验证码情况下可以跑满下行网速(对方网站条件允许)，开启验证时候不要太快,太快没用,验证码速度跟不上.
    2. login_config下面的data定义了提交数据的字段，账户密码验证码，只需要填写value
    3. 像有的还需要加动作`action=login`或者`token=xxxxx`，直接填写key，value进去，示例没用的字段可以删掉
    4. isPayload意思是因为有的网站提交直接是json格式，这样的话打开它
    5. login_fail 里面含有失败的特征匹配
    6. debug描述了所有输出都打印不管失败等情况
    7. page_contain_str 是包含这些字符就登录失败,status 状态码同理
    8. load_verify_code_url 是加载对方验证码的url
    9. verify_api是验证码识别接口的url，这里我用自己的，识别率很高，你也可以定义自己的，post字段内容就得换
---
---
### UpdateTime 2021/1/28 14：07
    1. 增加日志输出log，美化以下console输出
    2. 对于获取验证码的源地址，增加头内容image判断，不是验证码（waf，反爬）异常退出
    3. 其他优化

#### 目前密码都是明文提交，有的情况下是md5，自己可以将密码转换完成放到password.txt
#### BUG慢慢慢慢慢慢慢慢来 v1.1.0
#### LastUpdateTime 2021/1/28 14：07