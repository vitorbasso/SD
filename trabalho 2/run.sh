#!/bin/bash
clear
kill $(ps aux | grep python | grep server.py | awk '{print $2}')
./compile.sh
python3 server.py