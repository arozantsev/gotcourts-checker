# GotCourts Checker

Simple utility to check the availability of courts using the Public GotCourts API.

## Installation

In oder to install the package in you python environment, run the following from the code root:
```
pip install -e .
```

## Check availabile slots

In order to check available slots
```
python -m gotcourts.get_empty_slots --club=mythenquai --weekdays="sat, sun" --ndays=14
```

# Docker 

## Build

```
docker build -t gotcourts-checker:0.0.1 . -f .\docker\Dockerfile
```