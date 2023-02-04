#!/bin/bash

Xvfb :99 -nolisten tcp &
gunicorn -b 0.0.0.0:8000 flask_app:app;