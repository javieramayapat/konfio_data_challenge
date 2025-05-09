FROM jupyter/all-spark-notebook

COPY requirements.txt /tmp/

USER root

RUN python -m venv /venv
RUN /venv/bin/pip install --upgrade pip
RUN pip install -r /tmp/requirements.txt