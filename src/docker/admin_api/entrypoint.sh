#!/bin/bash
until cd ${PROJECT_BASE_DIR}
do
    echo "Waiting for server volume..."
done

echo "Making migrations"
until python3 ${PROJECT_BASE_DIR}/manage.py migrate
do
    echo "Waiting for db to be ready..."
    sleep 3
done
echo "All migrations applied"
cd ${PROJECT_BASE_DIR}


python3 ${PROJECT_BASE_DIR}/manage.py collectstatic --noinput
python3 ${PROJECT_BASE_DIR}/manage.py runserver 0.0.0.0:8000
