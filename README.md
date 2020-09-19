# Megadlbot aka Megatron:
Megatron was a telegram file management bot that helped a lot of users, specially movie channel managers to upload their files to telegram by just providing a link to it. The project initially started as roanuedhuru_bot which lately retired and came back as Megatron which was a side project of the famous Maldivian Telegram community - @Baivaru until it retired.

Megatron is a project that is very close to my heart - me being the whole brain who developed it since the very beginning and as you are aware, for the cause of its life span the bot was never opensource unlike many other telegram bots which did a similar job. You had asked for its source for long enough I though I am not just going to give the source but build the whole thing from scratch at YouTube with you guys. 

> [Youtube Playlist](https://www.youtube.com/playlist?list=PLApP3aDELGhvQqPcA_DsTSt-sA0v2OkqP)

## Important libraries used by the application:
1. [aiohttp](https://docs.aiohttp.org/en/latest/client.html)
2. [aiofiles](https://github.com/mosquito/aiofile)
3. [pymongo](https://github.com/mongodb/mongo-python-driver)
4. [pyrogram](https://docs.pyrogram.org/)
5. [tgcrypto](https://docs.pyrogram.org/topics/tgcrypto)

The application makes use of [MongoDB](https://www.mongodb.com/) for its database, also uses [ffprobe](https://ffmpeg.org/ffprobe.html) from ffmpeg for generating media info.

## Cloning and running:
1. Installation of DB

---
### Ubuntu:
```
sudo apt update
sudo apt install -y mongodb

# create a admin user and assign it roles
mongo
use admin
db.createUser({user:"admin", pwd:"password", roles:[{role:"root", db:"admin"}]})
exit

# edit the YAML config file with your favorite editor to enable authentication on DB instance
vim /etc/mongodb.conf

#Add these lines at the bottom of the YAML config file:
auth=ture

# now save the file and once its closed restart mongo service:
service mongod restart
```

### Windows:
a. Download the installer from [here](https://www.mongodb.com/try/download/community?tck=docs_server), and run it. \
b. Follow the MongoDB Community Edition installation wizard. \
c. Create a admin user and assign it roles:
```
# I assume you had used the default location to install.
# To connect a mongo.exe shell to the MongoDB instance, open another Command Interpreter with Administrative privileges and run:
"C:\Program Files\MongoDB\Server\4.4\bin\mongo.exe"
use admin
db.createUser({user:"admin", pwd:"password", roles:[{role:"root", db:"admin"}]})
exit
```
d. Stop the Mongo `MongoDB Server (MongoDB)` service from services.msc. \
e. Edit the Yamal Config file - `mongodb.cfg` located at `C:\Program Files\MongoDB\Server\4.4\bin` with your favorite editor and add the following lines:
```
security:
  authorization: enabled
```
f. Save the file and close it, also start the `MongoDB Server (MongoDB)` service that we stopped at services.msc

---


2. Installation of ffmpeg: \
a. Ubuntu: `apt install -y ffmpeg`. \
b. Windows: A full documentation of how to is [here](https://www.wikihow.com/Install-FFmpeg-on-Windows).
> Also I had shown this on my [video](https://www.youtube.com/watch?v=MMRtEvGpzdk)

---

3. `git clone https://github.com/eyaadh/megadlbot_oss.git`, to clone and the repository.
4. `cd megadlbot_oss/`, to enter the directory.
5. `pip3 install -r requirements.txt`, to install python libraries/dependencies/requirements for the project.

----
6. Create a new `config.ini` using the sample available at `mega/working_dir/config.ini.sample` at `mega/working_dir/`.
```
# Here is a sample of config file and what it should include:
[pyrogram]
# More info on API_ID and API_HASH can be found here: https://docs.pyrogram.org/intro/setup#api-keys
api_id = 
api_hash = 

[plugins]
root = mega/telegram/plugins

[bot-configuration]
# More info on Bot API Key/token can be found here: https://core.telegram.org/bots#6-botfather
api_key = 
session = megadlbot
# Watch this video to understand what the dustbin is: https://www.youtube.com/watch?v=vgzMacnI5Z8
dustbin = 
allowed_users = [123123123, 321321321]
# a list of user ids who are allowed to use this bot

[database]
# In this section db_host is the address of the machine where the MongoDB is running, if you are running 
# both the bot and Mongo on same machine leave it as local host.
# db_username and db_password are the username and password we assigned roleas with at the first step 
# while we installed Database
db_host = localhost
db_username = admin
db_password = 
db_name = megadlbot
```

---

7.  Run with `python3.8 -m mega`, stop with <kbd>CTRL</kbd>+<kbd>C</kbd>.
> It is recommended to use [virtual environments](https://docs.python-guide.org/dev/virtualenvs/) while running the app, this is a good practice you can use at any of your python projects as virtualenv creates an isolated Python environment which is specific to your project.


### The Easy Way:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Before clicking the Deploy button make sure you have the following details with you too:
1. Create a free account on cloud.mongodb.com (This is for the DB and you need its details for the config file as explained above, also keep a note that if you host mongoDB community edition on your own its totally free otherwise you might have limitations).
2. Create a Telegram channel (This one for the dustbin. As mentioned above watch this [video](https://www.youtube.com/watch?v=vgzMacnI5Z8) to understand what the dustbin is.)
3. Well as obvious as it can be create a bot with @BotFather, also get your API ID and API Hash from my.telegram.org.  
