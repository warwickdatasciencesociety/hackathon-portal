import mysql.connector
import os
import sys
import hashlib
from dotenv import load_dotenv
import datetime
load_dotenv()

choice = input("WARNING: WILL OVERWRITE ANY SAVED DATA ARE YOU SURE YOU WANT TO RUN? [y/n]")
if choice == "y":
    confirm = input("ARE YOU SURE? [y/n]")
    if confirm == "y":
        print("proceeding")
    else:
        sys.exit(0)
else:
    sys.exit(0)
mydb = mysql.connector.connect(
    host="127.00.00.1",
    port="32000",
    user="root",
    password="root"
)

mycursor = mydb.cursor()


mycursor.execute("SHOW DATABASES")
flag = False
for x in mycursor:
    if 'hackathon_portal' in x:
        flag = True


if not flag:
    mycursor.execute("CREATE DATABASE hackathon_portal")

mycursor.execute("USE hackathon_portal")
mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")
mycursor.execute("DROP TABLE IF EXISTS admin")
mycursor.execute("DROP TABLE IF EXISTS team")
mycursor.execute("DROP TABLE IF EXISTS userteam")
mycursor.execute("DROP TABLE IF EXISTS user")
mycursor.execute("DROP TABLE IF EXISTS submission")
mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")
mycursor.execute(
    "CREATE TABLE admin(admin_id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(30), password BLOB, salt BLOB)")
mycursor.execute(
    "CREATE TABLE team(team_id INT PRIMARY KEY AUTO_INCREMENT, teamname VARCHAR(30))")
mycursor.execute(
    "CREATE TABLE user(user_id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(30), password BLOB, salt BLOB)")
mycursor.execute(
    "CREATE TABLE userteam(userteam_id INT PRIMARY KEY AUTO_INCREMENT, team_id INT, user_id INT, FOREIGN KEY(team_id) REFERENCES team(team_id), FOREIGN KEY(user_id) REFERENCES user(user_id))")
mycursor.execute(
    "CREATE TABLE submission(submission_id INT PRIMARY KEY AUTO_INCREMENT, upload_time DATETIME, team_id INT, user_id INT, score FLOAT, tag VARCHAR(100), FOREIGN KEY(team_id) REFERENCES team(team_id), FOREIGN KEY(user_id) REFERENCES user(user_id))")
mycursor.execute("SHOW TABLES")

for x in mycursor:
    print(x)

# USERS
def create_user(username, password):
    sql = "INSERT INTO user (username, password, salt) VALUES (%s, %s, %s)"
    salt = os.urandom(32)
    print(salt)
    key = hashlib.pbkdf2_hmac(
        'sha256',  # The hash digest algorithm for HMAC
        password.encode('utf-8'),  # Convert the password to bytes
        salt,  # Provide the salt
        100000  # It is recommended to use at least 100,000 iterations of SHA-256
    )
    # print(key.decode('utf-8'))
    val = (username, key, salt)
    mycursor.execute(sql, val)
create_user('test', 'root')
create_user('john', 'root')
mycursor.execute("INSERT INTO team (teamname) VALUES ('Null Model')")
mycursor.execute("INSERT INTO team (teamname) VALUES ('Baseline Model')")
mycursor.execute("INSERT INTO userteam (team_id, user_id) VALUES (1,1)")
mycursor.execute("INSERT INTO userteam (team_id, user_id) VALUES (2,2)")
now = datetime.datetime(2009,5,5)
str_now = now.date().isoformat()
mycursor.execute("INSERT INTO submission (upload_time, team_id, user_id, score, tag) VALUES ('2020-11-13 12:00:00', 1, 1, 0.0219, 'demo')")
mycursor.execute("INSERT INTO submission (upload_time, team_id, user_id, score, tag) VALUES ('2020-11-13 12:00:00', 2, 2, 0.0269, 'demo')")

mydb.commit()
