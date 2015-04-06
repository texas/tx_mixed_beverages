FROM ubuntu:14.04
MAINTAINER Chris <c@crccheck.com>

RUN apt-get update -qq
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  # python
  python2.7 python-dev python-pip \
  # postgis
  libpq-dev libgeos-dev \
  # node
  nodejs nodejs-legacy npm \
  > /dev/null

RUN pip install --upgrade "pip<6.0"

RUN npm config set color false; \
  npm config set loglevel warn; \
  npm install -g grunt-cli --no-color

ADD . /app
WORKDIR /app

RUN pip install --quiet -r /app/requirements.txt

RUN npm install > /dev/null
RUN grunt build --no-color

RUN python manage.py collectstatic --noinput -v0

EXPOSE 8080
CMD ["waitress-serve", "mixed_beverages.wsgi:application"]
