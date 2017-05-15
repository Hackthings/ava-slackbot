# ava-slackbot

[![Build Status](https://travis-ci.org/ImageIntelligence/ava-slackbot.svg?branch=master)](https://travis-ci.org/ImageIntelligence/ava-slackbot)

**Welcome to ava-slackbot!**

This project is our in house Slackbot, allowing us to interact with the Image Intelligence API (Ava).

## Installation

1. Clone the project:

    ```bash
    git clone git@github.com:ImageIntelligence/ava-slackbot.git
    ```

1. Specify the required environment variables:

    Create a file at the root of this project called `local.env.list` with the following contents

    ```bash
    AVA_API_ENDPOINT=https://api.imageintelligence.com
    AVA_API_VERSION=v1
    AVA_CLIENT_ID=
    AVA_CLIENT_SECRET=
    SLACK_API_TOKEN=
    SLACK_WHITELIST_CHANNELS=
    ```

    See the Image Intelligence [docs](https://imageintelligence.com/docs) for `AVA_CLIENT_ID` and `AVA_CLIENT_SECRET`.

1. Install docker and docker-compose:

    ```bash
    brew install docker-compose
    brew install cask
    brew cask install docker
    brew cask install docker-toolbox
    ```

1. Start the container:

    ```bash
    docker-compose up
    ```

## Development

1. (optional) Setup your host's local environment (IDE support):

    ```bash
    mkvirtualenv --python=/usr/local/bin/python3 ava-slackbot
    pip install -r requirements.txt
    ```

1. Clean your project of cache files:

    ```bash
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    ```

1. PEP8 your Python code:

    ```
    pep8 ./ --ignore=E501,E701
    ```
