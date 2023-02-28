#!/bin/sh
source env/bin/activate
git checkout develop
git pull origin develop
pip install -r requirements.txt
