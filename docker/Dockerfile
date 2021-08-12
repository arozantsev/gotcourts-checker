# Builder image
# separate builder image is required (to reduce final docker image size), because some python
# dependencies might not be compiled for all platforms (e.g ARM)

FROM python:3.8-slim-buster as builder
RUN mkdir /gotcourts
WORKDIR /gotcourts
ADD gotcourts gotcourts
ADD setup.py setup.py
RUN apt-get update -qq && apt-get install -y build-essential
RUN pip install .

# runtime image

FROM python:3.8-slim-buster

COPY --from=builder /gotcourts /gotcourts
COPY --from=builder /usr/local/lib/python3.8/site-packages /usr/local/lib/python3.8/site-packages
WORKDIR /gotcourts
RUN pip install .
ENV PYTHONPATH=/gotcourts/gotcourts:$PYTHONPATH
ENTRYPOINT [ "python", "/gotcourts/gotcourts/run.py" ]
