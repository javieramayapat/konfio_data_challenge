FROM jupyter/all-spark-notebook
COPY dist /tmp/
COPY requirements.txt /tmp/

USER root

RUN python -m venv /venv
RUN /venv/bin/pip install --upgrade pip
RUN pip install /tmp/konfio_extractors-0.1-py3-none-any.whl
RUN pip install -r /tmp/requirements.txt