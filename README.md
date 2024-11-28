# Jd

基于Flask 3 + Flask-SQLAlchemy 3

Python3.7+

提供简单的api


## 代码

### 结构说明

+ jd
  + services 业务层
  + models 模型层（定义类对象以及各类sql操作）
  + views
    + api 接口层
+ dbrt 数据库表结构
+ utils 工具类
+ config.py 项目配置文件
+ requirements.txt  项目依赖
+ web.py  项目入口

### API

#### http状态码说明

| http code | 说明 | Response结构 | Response说明 |
|---|---|---|---|
| 200 |  | {"err_code":0,"err_msg":"","payload":{}} | err_code > 0 表示业务非正常情况，需要对err_code作处理 |
| 400 | 请求异常：参数错误等 | {"err_code":10001,"err_msg":"","payload":{}} | 解析 err_msg toast展示 |
| 401 | 鉴权 | {"err_code":0,"err_msg":"","payload":{}} | 处理登录 |
| 500 | 服务器内部错误 | {"err_code":0,"err_msg":"","payload":{}} | 解析 err_msg toast展示 |


### 数据库会话提交

数据库会话提交只允许在  tasks、jobs、views层操作，其它层不允许出现数据库提交操作

### 数据库事务


## 开发

### 初始化开发环境

```shell
pip install -r requirements.txt
```

### 一键启动
```shell
bash start.sh -a
```

### 重启celery
```shell
bash start.sh -c
```

### 重启web
```shell
bash start.sh -w
```

### 一键关闭
```shell
bash stop.sh

```

### 运行爬虫celery
```shell
celery -A scripts.worker:celery worker -Q jd.celery.first --loglevel=info
```
### 运行tg celery
```shell
celery -A scripts.worker:celery worker -Q jd.celery.telegram -c 1 --loglevel=info
```
### 运行beat
```shell
celery -A scripts.worker:celery beat  --loglevel=info
```


### 运行web
```shell
python web.py
```

### 运行某个脚本
```shell
python -m scripts.job test
```

### 获取Tg配置, 获取api_id、api_hash,并在config.py中配置
```shell
https://my.telegram.org/auth
```


### tg初始化，用户生成session文件，tg操作前请先操作该命令，生成的session文件在static/utils目录下
```shell
python -m scripts.job init_tg
```
