#!/bin/bash

echo "uwsgi" `uwsgi --version`
echo "circusd" `circusd --version`
django-admin env
