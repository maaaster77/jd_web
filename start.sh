#!/bin/bash

# 停止flask
pid=$(ps aux | grep 'Python -m web' | grep -v grep | awk '{print $2}')
if [ -z "$pid" ]; then
  echo "Flask 未运行"
else
  kill -9 $pid
  echo "已杀死 Flask 进程: $pid"
fi

# 停止celery
pid=$(ps aux | grep celery | grep -v grep | awk '{print $2}')
if [ -z "$pid" ]; then
  echo "Celery 未运行"
else
  kill -9 $pid
  echo "已杀死 Celery 进程: $pid"
fi


# 启动celery
echo "启动celery"
nohup celery -A scripts.worker:celery worker -Q jd.celery.first --loglevel=info > log/celery_out.txt 2>&1 &

echo "启动flower"
nohup celery -A scripts.worker:celery flower --loglevel=info --persistent=True --db="flower_db" > log/celery_flower.txt 2>&1 &
echo "celery 监控: http://127.0.0.1:5555"



# 启动flask
echo "启动web"
nohup python -m web   > log/flask_out.txt 2>&1 &
echo "web: http://127.0.0.1:8080"


echo 'End'