# GotCourts Checker

Simple utility to check the availability of courts using the Public GotCourts API that is intended for personal use.

## Python environment

In order to run the code you use a local python environment with python version >= ``3.6``

### Installation

In oder to install the package in you python environment, run the following from the code root:
```
pip install .
```

### Check availabile slots

In order to check available slots
```
python -m gotcourts.run --club=mythenquai --weekdays="sat, sun" --ndays=14
```

## Docker

Alternatively, instead of using a python environment, there is a possibility to run the code in docker. For that you need to have docker installed on you machine.

### Build

In order to build the docker image run:
```
docker build -t gotcourts-checker:0.1.0 . -f .\docker\Dockerfile
```

### Check available slots

You can then check available slots by running:
```
docker run --rm -it gotcourts-checker:0.1.0 --weekdays="sat, sun" --ndays=14
```

## Telegram notification

In order to send notification to a specific channel in telegram about the court availability you need to:

1. Create a configuration file `config.yaml` with the list of telegram channel IDs as follows:
    ```
    chat_ids:
    - <telegram_chat_id_1>
    - <telegram_chat_id_2>
    ```

2. pass telegram bot token and config to the script as follows:
    ```
    python -m gotcourts.run --club=mythenquai --weekdays="sat, sun" --ndays=14 --tconf=<path to config.yaml> --ttoken="<telegram bot token>"
    ```

## Telegram Bot service

There is a possibility to run the code as a service that listens and responses to requests from the a telegram bot.

1. Set run mode to ``service`` and pass telegram bot token and config to the script as follows:
    ```
    python -m gotcourts.run --mode=service --ttoken="<telegram bot token>"
    ```

You can then use the following commands, when interacting with Telegram Bot:
1. /start - command to print the welcome message
2. /check - command to check the available slots in a certain tennis club for a certain weekday. You can use this command as follows:
    ```
    /check <tennis club alias (mythenquai)> <week days (sat sun)>
    ```
