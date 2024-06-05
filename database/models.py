from mongoengine import Document, StringField, BooleanField

class Contact(Document):
    username = StringField(required=True)
    email = StringField(required=True)
    sent = BooleanField(default=False)
    phone_number = StringField()
    preferred_contact_method = StringField(
        choices=["email", "sms"],
        default="email"
    )

    meta = {'collection': 'contacts'}
