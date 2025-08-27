from mongoengine import Document, StringField, ListField, IntField

class PostMetadata(Document):
    post_id = IntField(required=True, unique=True) 
    tags = ListField(StringField(), default=list)
    category = StringField()
    meta = {'collection': 'post_metadata'}