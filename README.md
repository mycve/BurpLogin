### 使用方法  python3执行 main.py + 配置好的文件 即可！
    python3 main.py NoVerify.json
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
    3. 像有的还需要加动作action=login或者token=xxxxx，直接填写key，value进去，示例没用的字段可以删掉
    4. isPayload意思是因为有的网站提交直接是json格式，这样的话打开它
    5. login_fail 里面含有失败的特征匹配
    6. debug描述了所有输出都打印不管失败等情况
---
#### BUG慢慢来 v1.0.2
####         by:        2021/1/21 11：34