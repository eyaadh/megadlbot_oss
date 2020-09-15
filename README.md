# Megadlbot:
Megatron was a telegram file management bot that helped a lot of users, specially movie channel managers to upload their files to telegram by just providing a link to it. The project initially started as roanuedhuru_bot which lately retired and came back as Megatron which was a side project of the famous Maldivian Telegram community - @Baivaru until it retired.

Megatron is a project that is very close to my heart - me being the whole brain who developed it since the very beginning and as you are aware, for the cause of its life span the bot was never opensource unlike many other telegram bots which did a similar job. You had asked for its source for long enough I though I am not just going to give the source but build the whole thing from scratch at YouTube with you guys. 

> [Youtube Playlist](https://www.youtube.com/playlist?list=PLApP3aDELGhvQqPcA_DsTSt-sA0v2OkqP)

## Important libraries used by the application and what they do:
1. [aiohttp](https://docs.aiohttp.org/en/latest/client.html)
2. [aiofiles](https://github.com/mosquito/aiofile)
3. [pymongo](https://github.com/mongodb/mongo-python-driver)
4. [pyrogram](https://docs.pyrogram.org/)
5. [tgcrypto](https://docs.pyrogram.org/topics/tgcrypto)

The application makes use of [MongoDB](https://www.mongodb.com/) for its database, also uses [ffprobe](https://ffmpeg.org/ffprobe.html) from ffmpeg for generating media info.

## Cloning and running:
1. Installation of DB
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

2. Installation of ffmpeg: \
a. Ubuntu: `apt install -y ffmpeg`. \
b. Windows: A full documentation of how to is [here](https://www.wikihow.com/Install-FFmpeg-on-Windows).
