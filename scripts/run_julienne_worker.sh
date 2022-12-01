#!/bin/bash


cd /app
celery -A julienne worker --loglevel INFO 

