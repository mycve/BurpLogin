## 使用方法    python3执行 main.py + 配置好的文件   即可！
    python3 main.py NoVerify.json
--- 

### 首次安装依赖
    pip3 install gevent requests

---
#### speed 是调节速度的，适当调节没验证码情况下可以跑满下行网速(对方网站条件允许)，开启验证时候不要太快,太快没用,验证码速度跟不上.
####          剩下的自己看看字段意思吧，毕竟一天完成的，就发出来了，下一版优化

#### login_config下面的data定义了提交数据的字段
#### isPayload意思是因为有的网站提交直接是json格式，这样的话打开它
#### login_fail 里面含有失败的特征匹配
#### debug描述了所有输出都打印不管失败等情况




#### 内测，bug勿催 v1.0.2
