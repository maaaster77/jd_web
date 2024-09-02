#!/bin/bash

# 停止flask
pid=$(ps aux | grep 'Python -m web' | grep -v grep | awk '{print $2}')
if [ -z "$pid" ]; then
  echo "Flask 未运行"
else
  kill -9 $pid
  echo "已关闭 Flask 进程: $pid"
fi

# 停止celery
pid=$(ps aux | grep celery | grep -v grep | awk '{print $2}')
if [ -z "$pid" ]; then
  echo "Celery 未运行"
else
  kill -9 $pid
  echo "已关闭 Celery 进程: $pid"
fi

# 停止tg聊天抓取job
pid=$(ps aux | grep 'chat_history' | grep -v grep | awk '{print $2}')
if [ -z "$pid" ]; then
  echo "聊天抓取脚本 未运行"
else
  kill -9 $pid
  echo "已关闭 聊天抓取脚本 进程: $pid"
fi


# 启动celery
echo "启动celery first"
nohup celery -A scripts.worker:celery worker -Q jd.celery.first --loglevel=info > log/celery_out.txt 2>&1 &

echo "启动celery telegram"
nohup celery -A scripts.worker:celery worker -Q jd.celery.telegram -c 1 --loglevel=info > log/celery_telegram_out.txt 2>&1 &

# echo "启动flower"
# nohup celery -A scripts.worker:celery flower --loglevel=info --persistent=True --db="flower_db" > log/celery_flower.txt 2>&1 &


# 启动flask
echo "启动web"
nohup python -m web   > log/flask_out.txt 2>&1 &
echo "web: http://127.0.0.1:8981"

# # 启动tg聊天记录抓取ojb
echo "启动tg聊天记录抓取ojb"
nohup python -m scripts.job chat_history > log/chat_history.txt 2>&1 &

# echo 'End'
