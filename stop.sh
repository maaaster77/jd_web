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