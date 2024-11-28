#!/bin/bash

# 帮助信息
usage() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  -w              启动web"
  echo "  -c                启动Celery 服务"
  echo "  -a              执行所有启动"
  echo "  -h             显示帮助信息"
  exit 1
}

# 处理命令行参数
while [[ $# -gt 0 ]]; do
  case $1 in
    -w)
      web=true
      shift
      ;;
    -c)
      celery_flag=true
      shift
      ;;
    -a)
      web=true
      celery_flag=true
      shift
      ;;
    -h)
      usage
      ;;
    *)
      echo "Unknown option: $1"
      usage
      ;;
  esac
done
# 从 Git 拉取最新代码
echo "更新代码"
git pull

# 加载 conda 初始化脚本
echo "加载 conda 初始化脚本"
export PTAH = "/home/ubuntu/miniconda3"
eval "$(conda shell.bash hook)"

# 激活 conda 环境
echo "激活环境: sdweb"
conda activate sdweb

# celery
if [ "${celery_flag}" = "true" ]; then
  pid=$(ps aux | grep celery | grep -v grep | awk '{print $2}')
  if [ -z "$pid" ]; then
    echo "Celery 未运行"
  else
    kill -9 $pid
    echo "已关闭 Celery 进程: $pid"
  fi
  echo "清理进行中job"
  python -m scripts.job once.deal_job_queue
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
