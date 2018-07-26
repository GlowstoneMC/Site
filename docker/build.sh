#!/bin/bash

# Build and deploy on master branch
if [[ $CIRCLE_BRANCH == 'master' ]]; then

    echo "Connecting to docker hub"
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

    echo "Building: Celery..."
    docker build -t gdude2002/glowstone-celery:latest -f docker/celery/Dockerfile .

    echo "Pushing image to Docker Hub..."
    docker push gdude2002/glowstone-celery:latest

    echo "Building: Site..."
    docker build -t gdude2002/glowstone-site:latest -f docker/site/Dockerfile .

    echo "Pushing image to Docker Hub..."
    docker push gdude2002/glowstone-site:latest
else
    echo "Skipping deploy; not on master"
fi
