#!/bin/bash

# 帮助信息
usage() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  --web             启动web"
  echo "  --celery          启动Celery 服务"
  echo "  --all              执行所有启动"
  echo "  --help             显示帮助信息"
  exit 1
}

# 处理命令行参数
while [[ $# -gt 0 ]]; do
  case $1 in
    --web)
      web=true
      shift
      ;;
    --celery)
      celery=true
      shift
      ;;
    --all)
      web=true
      celery=true
      shift
      ;;
    --help)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done


# celery
if [ "${celery}" = "true" ]; then
  pid=$(ps aux | grep celery | grep -v grep | awk '{print $2}')
  if [ -z "$pid" ]; then
    echo "Celery 未运行"
  else
    kill -9 $pid
    echo "已关闭 Celery 进程: $pid"
  fi
  echo "启动 Celery Worker"
  nohup celery -A scripts.worker:celery worker -Q jd.celery.first --loglevel=info > log/celery_out.txt 2>&1 &
  echo "启动 Celery Telegram Worker"
  nohup celery -A scripts.worker:celery worker -Q jd.celery.telegram -c 1 --loglevel=info > log/celery_telegram_out.txt 2>&1 &
  echo "启动 Celery Beat"
  nohup celery -A scripts.worker:celery beat --loglevel=info > log/celery_beat.txt 2>&1 &
  #  echo "启动 Flower"
#  nohup celery -A scripts.worker:celery flower --loglevel=info --persistent=True --db="flower_db" > log/celery_flower.txt 2>&1 &
fi


# web
if [ "${web}" = "true" ]; then
  pid=$(lsof -i :8981 -t)
  if [ -z "$pid" ]; then
    echo "Flask 未运行"
  else
    kill -9 $pid
    echo "已关闭 Flask 进程: $pid"
  fi
  echo "启动 Flask"
  nohup python -m web > log/flask_out.txt 2>&1 &
  echo "Web: http://127.0.0.1:8981"
fi


echo 'End'
