FROM python:3-slim

RUN mkdir /gotcourts
WORKDIR /gotcourts
ADD gotcourts gotcourts
ADD setup.py setup.py
RUN pip install . 
ENV PYTHONPATH=/gotcourts/gotcourts:$PYTHONPATH
ENTRYPOINT [ "python", "/gotcourts/gotcourts/get_empty_slots.py" ]