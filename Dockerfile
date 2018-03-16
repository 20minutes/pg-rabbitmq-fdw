FROM postgres:10.1

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y -q make gcc git postgresql-server-dev-10 python-dev python-setuptools python-pip

RUN git clone https://github.com/Kozea/Multicorn /tmp/multicorn && \
    cd /tmp/multicorn && \
    git checkout v1.3.4 && \
    make install

RUN mkdir /tmp/pg-rabbitmq-fdw

ADD . /tmp/pg-rabbitmq-fdw

RUN cd /tmp/pg-rabbitmq-fdw && \
    pip install -r requirements.txt && \
    python setup.py install
