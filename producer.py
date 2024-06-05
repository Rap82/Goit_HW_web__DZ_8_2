import random
import sys
import pika

from faker import Faker
from logger import logger
from database.models import Contact
from database.connect import get_database
from brocker_connect import connect



def make_contacts(amount: int) -> list:
    fake = Faker()
    Faker.seed(1234) 
    contacts = []
    for _ in range(amount):
        username = fake.user_name()
        domain = fake.domain_name()  
        email = username.lower() + "@" + domain 
        contact = Contact(
            username=username,
            email=email,
            phone_number=fake.phone_number(),
            preferred_contact_method=random.choice(["email", "sms"])
        )
        contacts.append(contact)
    return contacts

if __name__ == "__main__":
    db = get_database().client
   
    try:
        channel = connect()
    except pika.exceptions.AMQPConnectionError as e:
        logger.error("Failed to connect to RabbitMQ.")
        logger.error(str(e))
        sys.exit(1)

    # Очищення бази 
    Contact.objects().delete()

    # Наовнення бази
    for contact in make_contacts(100):
        contact.save()

    logger.info("<== Database filled with contacts. ==>")

    # Створення черг в брокері
    channel.queue_declare(queue='email_queue')
    channel.queue_declare(queue='sms_queue')


    # Очищення черг перед наповненням
    channel.queue_purge(queue='email_queue')
    channel.queue_purge(queue='sms_queue')


    # Отримання даних з mongo
    contacts = Contact.objects.all()


    for contact in contacts:
        match contact.preferred_contact_method:
            case "email":
                channel.basic_publish(exchange='',
                                    routing_key='email_queue', 
                                    body=str(contact.id).encode())
            case "sms":
                channel.basic_publish(exchange='', 
                                    routing_key='sms_queue', 
                                    body=str(contact.id).encode())


    logger.info("<== Messages sent to the appropriate queues. ==>")
    channel.close()
    db.close()