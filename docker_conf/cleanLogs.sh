#!/bin/bash

LOG_DIR=/client/data/log
find $LOG_DIR -mtime +30 | xargs -r rm
find $LOG_DIR -type f -not \( -iname '*.gz' -or -iname 'client.log' \) -exec gzip -9 "{}" \;