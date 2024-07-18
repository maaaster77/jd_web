
# 路由前缀
API_PREFIX = '/api'

# mysql相关配置
SQLALCHEMY_ECHO = True
SQLALCHEMY_ENABLE_POOL = False
SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:Hzc123123..@127.0.0.1:3306/jd?charset=utf8mb4'
SQLALCHEMY_BINDS = {
}

# jwt 配置
JWT_SECRET_KEY = "hello!jd"
JWT_ACCESS_TOKEN_EXPIRES = 7 * 24 * 60 * 60

SESSION_SECRET_KEY = "hello!jd"