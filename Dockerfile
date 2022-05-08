# base image
FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=New_York/America
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3.9 python3.9-dev python3-pip

RUN pip3 install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry export --without-hashes -f requirements.txt > requirements.txt

ENV PYTHONUNBUFFERED=1

RUN pip3 install -r requirements.txt

# exposing default port for streamlit
EXPOSE 8501

# making directory of app
WORKDIR /streamlit-docker

# copying all files over
COPY . .

# cmd to launch app when container is run
CMD streamlit run app.py

# streamlit-specific commands for config
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN mkdir -p /root/.streamlit
RUN bash -c 'echo -e "\
[general]\n\
email = \"\"\n\
" > /root/.streamlit/credentials.toml'

RUN bash -c 'echo -e "\
[server]\n\
enableCORS = false\nserver.enableXsrfProtection=false\n\
" > /root/.streamlit/config.toml'