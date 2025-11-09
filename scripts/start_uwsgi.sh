#!/bin/bash

# Roamio uWSGI 启动脚本

cd /home/acs/roamio

# 杀掉旧进程
pkill -9 -f uwsgi

# 等待进程完全退出
sleep 2

# 启动 uWSGI
uwsgi --ini scripts/uwsgi.ini

echo "uWSGI started successfully!"

