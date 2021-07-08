# GotCourts Checker

Simple utility to check the availability of courts using the Public GotCourts API.

## Installation

In oder to install the package in you python environment, run the following from the code root:
```
pip install .
```

## Check availabile slots

In order to check available slots
```
python -m gotcourts.get_empty_slots --club=mythenquai --weekdays="sat, sun" --ndays=14
```

# Docker 

Instead of using a python environment there is a possibility to run the code in docker. For that you need to have docker installed on you machine.

## Build

In order to build the docker image run:
```
docker build -t gotcourts-checker:0.0.1 . -f .\docker\Dockerfile
```

## Check available slots

You can then check available slots by runnig:
```
docker run --rm -it gotcourts-crawler:0.0.1 --weekdays="sat, sun" --ndays=14
```
