#!/bin/bash

cat /RELEASE
exho "uwsgi `uwsgi --version`"
echo "Django `django-admin --version`"
