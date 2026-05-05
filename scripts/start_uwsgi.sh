#!/bin/bash

# Roamio uWSGI 启动脚本

cd /home/acs/roamio

# 杀掉旧进程（勿用 pkill -f uwsgi，会误匹配 deploy_uwsgi.sh 等脚本名）
if command -v pgrep >/dev/null 2>&1; then
  _u_pids="$(pgrep -x uwsgi 2>/dev/null || true)"
  if [[ -n "${_u_pids}" ]]; then
    # shellcheck disable=SC2086
    kill -9 ${_u_pids} 2>/dev/null || true
  fi
elif command -v killall >/dev/null 2>&1; then
  killall -9 uwsgi 2>/dev/null || true
fi
# 等待进程完全退出
sleep 2

# 启动 uWSGI
uwsgi --ini scripts/uwsgi.ini

echo "uWSGI started successfully!"

