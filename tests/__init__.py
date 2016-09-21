import unittest
import pika
import psycopg2

class RabbitmqFDWTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(RabbitmqFDWTest, self).__init__(*args, **kwargs)

        self.host = 'localhost'
        self.port = int('5672')
        self.user = 'test'
        self.password = 'test'
        self.queue = 'indexing'

        # define PG connexion
        self.pg_conn = psycopg2.connect("dbname=travis_ci_test user=postgres host=127.0.0.1")
        self.pg_cursor = self.pg_conn.cursor()

        # define rabbit connexion
        connection = pika.BlockingConnection(pika.URLParameters('amqp://{0}:{1}@{2}:{3}/%2F'.format(self.user, self.password, self.host, self.port)))
        self.rabbit_channel = connection.channel()

    def test1Insert(self):
        self.pg_cursor.execute("INSERT INTO tag (tag_id, label, slug) VALUES ('{0}', '{1}', '{2}')".format('c94e3e70-c5fa-4ea4-a708-d23903b26d50', 'Politic', 'politic'))
        self.pg_conn.commit()

        method_frame, header_frame, body = self.rabbit_channel.basic_get(self.queue)

        if method_frame:
            self.rabbit_channel.basic_ack(method_frame.delivery_tag)

            self.assertEqual('{"action": "insert", "table": "tag", "id": "c94e3e70-c5fa-4ea4-a708-d23903b26d50"}', body)
        else:
            self.fail('No message returned')

    def test2Update(self):
        self.pg_cursor.execute("UPDATE tag SET label = '{0}' WHERE tag_id = '{1}'".format('Sport', 'c94e3e70-c5fa-4ea4-a708-d23903b26d50'))
        self.pg_conn.commit()

        method_frame, header_frame, body = self.rabbit_channel.basic_get(self.queue)

        if method_frame:
            self.rabbit_channel.basic_ack(method_frame.delivery_tag)

            self.assertEqual('{"action": "update", "table": "tag", "id": "c94e3e70-c5fa-4ea4-a708-d23903b26d50"}', body)
        else:
            self.fail('No message returned')

    def test3Delete(self):
        self.pg_cursor.execute("DELETE FROM tag WHERE tag_id = '{0}'".format('c94e3e70-c5fa-4ea4-a708-d23903b26d50'))
        self.pg_conn.commit()

        method_frame, header_frame, body = self.rabbit_channel.basic_get(self.queue)

        if method_frame:
            self.rabbit_channel.basic_ack(method_frame.delivery_tag)

            self.assertEqual('{"action": "delete", "table": "tag", "id": "c94e3e70-c5fa-4ea4-a708-d23903b26d50"}', body)
        else:
            self.fail('No message returned')

