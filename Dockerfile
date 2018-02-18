FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD src/requirements/install.pip /code/
RUN pip install -r install.pip
ADD . /code/
