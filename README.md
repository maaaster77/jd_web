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


### 运行web

```shell
python web.py
```
