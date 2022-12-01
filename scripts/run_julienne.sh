#!/bin/bash -ex

cd /app
echo running
python -m julienne tests/data/patient_example.json 100000
echo done
