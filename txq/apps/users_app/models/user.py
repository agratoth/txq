import os
import hashlib
import binascii

from pynsodm.rethinkdb_ext import BaseModel
from pynsodm.fields import StringField
from pynsodm.valids import valid_email
from pynsodm.handlers import salted_sha512_hash_password


class User(BaseModel):
    table_name = 'users'

    username = StringField()
    password = StringField(
        handler=salted_sha512_hash_password,
        is_sensitive=True)
    role = StringField(items=['admin', 'client'])
    status = StringField(items=['active', 'inactive'])

    @classmethod
    def get_by_username(cls, username):
        finded_users = User.find(username=username)
        if len(finded_users) > 0:
            return finded_users[0]
        return None

    def verify_password(self, password):
        salt = self.password[:64]
        stored_password = self.password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt.encode('ascii'), 100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password