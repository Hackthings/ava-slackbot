#!/usr/bin/env bash
set -e

docker build --tag imageintelligence/$APP_NAME:$DOCKER_TAG .

if [ $TRAVIS_BRANCH = 'develop' ] || [ $TRAVIS_BRANCH = 'master' ]; then
  docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
  docker push imageintelligence/$APP_NAME:$DOCKER_TAG
fi
