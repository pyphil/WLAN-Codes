import os
import hashlib
import sqlite3

user = input("User: ")
password = input("Password: ")

# Salt generieren und hash zu Passwort erzeugen
salt = os.urandom(32)
key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)

print(salt)
print(key)

# User, salt und hash in Datenbank speichern
verbindung = sqlite3.connect("wlan-code.db")
c = verbindung.cursor()
c.execute(""" CREATE TABLE account(user VARCHAR(20), salt BINARY(128),
            key BINARY(128))
            """)

c.execute(""" INSERT INTO account (user, salt, key) VALUES (?, ?, ?)
          """,
          (user, salt, key))
verbindung.commit()
