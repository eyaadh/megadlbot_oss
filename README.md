# Megadlbot aka Megatron:
Megatron was a telegram file management bot that helped a lot of users, it specifically helped movie channel managers to upload their files to telegram by just providing a link to it. The project initially started as roanuedhuru_bot which lately retired and came back as Megatron which was a side project of the famous Maldivian Telegram community - @Baivaru, until it retired.

Megatron is a project that is very close to my heart, me being the sole brains who developed it since the very beginning, and as you are aware, for the course of its life span the bot was never opensource unlike many other telegram bots which did a similar job. Many users beseeched to make it opensource so after I decided to kill the project I decided not just to make the source code public but to instead build the whole thing from scratch and upload it on YouTube. The purpose of this was to ensure that anyone could create their own bot based on this with ease and to ensure that the code was beautiful and easy to read. 

> [Youtube Playlist](https://www.youtube.com/playlist?list=PLApP3aDELGhvQqPcA_DsTSt-sA0v2OkqP)

## Important libraries used by the application:
1. [aiohttp](https://docs.aiohttp.org/en/latest/client.html)
2. [aiofiles](https://github.com/mosquito/aiofile)
3. [pymongo](https://github.com/mongodb/mongo-python-driver)
4. [pyrogram](https://docs.pyrogram.org/)
5. [tgcrypto](https://docs.pyrogram.org/topics/tgcrypto)
6. [Youtube-dl](https://github.com/ytdl-org/youtube-dl)
7. [google-api-python-client](https://github.com/googleapis/google-api-python-client)

The application makes use of [MongoDB](https://www.mongodb.com/) for its database, also uses [ffprobe](https://ffmpeg.org/ffprobe.html) from ffmpeg for generating media info.
Also optionally it makes use of [seedr](https://www.seedr.cc/) API to allow download torrents via the bot - however this is a user base setting, that end user needs to setup via options under /dldsettings

To make use of google API to generate google drive links for the files that you upload, you would be required to create a service account and share its key with the bot from the available options at /dldsettings, to generate this key make use of this step by step [documentation](https://support.google.com/a/answer/7378726?hl=en) or otherwise a much in depth detailed documentation [here](https://cloud.google.com/iam/docs/creating-managing-service-account-keys). Also I have shown this process on the 18th [Video](https://youtu.be/wOrmOvRhFsk?t=469) of the YouTube Series.

## Run on Docker 🐳
```You can simply ignore everything below if you choose to go with Docker Method```<br>
- [Docker Guide](DockerReadme.md)

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
auth=true

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

# for the following section fill in the FQDN with which end users can reach the host machine, bindaddress is the address of the adapter to bind with while running webserver and the port for the webserver to listen.
[web_server]
bind_address = 0.0.0.0
fqdn = localhost
port = 8080
```

---

7.  Run with `python3.9 -m mega`, stop with <kbd>CTRL</kbd>+<kbd>C</kbd>.
> It is recommended to use [virtual environments](https://docs.python-guide.org/dev/virtualenvs/) while running the app, this is a good practice you can use at any of your python projects as virtualenv creates an isolated Python environment which is specific to your project.


### Deploying on Heroku:

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Before clicking the Deploy button make sure you have the following details with you too:
1. Create a free account on cloud.mongodb.com (This is for the DB and you need its details for the config file as explained above, also keep a note that if you host mongoDB community edition on your own its totally free otherwise you might have limitations).
2. Create a Telegram channel (This one for the dustbin. As mentioned above watch this [video](https://www.youtube.com/watch?v=vgzMacnI5Z8) to understand what the dustbin is.) 
3. Well as obvious as it can be create a bot with @BotFather, also get your API ID and API Hash from my.telegram.org.  
