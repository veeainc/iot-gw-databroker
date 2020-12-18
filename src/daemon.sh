#!/bin/sh
################################################################################
# Copyright (C) Veea Systems Limited - All Rights Reserved.
# Unauthorised copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential. [2019-2020]
################################################################################

cd /app
source /app/myapp/venv3/bin/activate
python databroker.py &

while true
do
  echo sleeping...
  sleep 30
done

