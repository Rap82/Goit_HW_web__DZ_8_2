import pika

def connect():
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection( pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()
    return channel