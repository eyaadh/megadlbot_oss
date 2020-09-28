# Docker Guide For megadlbot 🐳 #

## Install docker ##
- Follow the official docker [installation guide](https://docs.docker.com/engine/install/ubuntu/)

## Install Docker-compose ##
- Easiest way to install docker-compose is <br>
```sudo pip install docker-compose```
- Also you can check other official methods of installing docker-compose [here](https://docs.docker.com/compose/install/)

## Run megadl ##
- We dont need to clone the repo (yeah Docker-compose does that for us)
- Setup configs
    - Download the sample config file <br>
        - ```mkdir megadl && cd megadl```
        - ```wget https://raw.githubusercontent.com/eyaadh/megadlbot_oss/dev/mega/working_dir/sampleConfigForDocker.ini.sample -O config.ini```
        - ```vim config.ini```
    - Download the yml file for docker-compose
        - ```wget https://raw.githubusercontent.com/eyaadh/megadlbot_oss/dev/docker-compose.yml```
- Finally start the bot <br>
```docker-compose up -d```
- Voila !! The bot should be running now <br>
Check logs with ```docker-compose logs -f```

## How to stop the bot ##
- Stop Command
    - This will just stop the containers. Built images won't be removed. So next time you can start with ``docker-compose start`` command <br>
    And it won't take time for building from scratch<br>
    ```docker-compose stop```
- Down command
    - You will stop and delete the bilt images also. So next time you have to do ``docker-compose up -d`` to start the bot<br>
    ```docker-compose down```