""" Install file for Postgres Elasticsearch Foreign Data Wrapper """
from setuptools import setup

if __name__ == '__main__':
    setup(
        name='pg_rabbitmq',
        description='PostgreSQL RabbitMQ Foreign Data Wrapper (write only)',
        version='1.0.1',
        author='20 Minutes',
        license='MIT',
        packages=['pg_rabbitmq'],
        url='https://github.com/20minutes/pg-rabbitmq-fdw',
        test_suite="tests"
    )
