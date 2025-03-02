
[![Discord](https://img.shields.io/discord/997761163020488815?color=7289DA&label=Discord&style=for-the-badge&logo=discord)](https://discord.gg/7hAUKKTyTd)
[![DockerHub](https://img.shields.io/badge/Docker-Hub-%23099cec?style=for-the-badge&logo=docker)](https://hub.docker.com/r/yoruio/membarr)
![Docker Pulls](https://img.shields.io/docker/pulls/yoruio/membarr?color=099cec&style=for-the-badge)
[![docker-sync](https://github.com/Yoruio/Membarr/actions/workflows/docker-sync.yml/badge.svg)](https://github.com/Yoruio/Membarr/actions/workflows/docker-sync.yml)

Membarr 
=================

Membarr is a fork of Invitarr that invites discord users to Plex and Emby. You can also automate this bot to invite discord users to a media server once a certain role is given to a user or the user can also be added manually.  

### Features

- Ability to invite users to Plex and Emby from discord 
- Fully automatic invites using roles 
- Ability to kick users from plex if they leave the discord server or if their role is taken away.
- Ability to view the database in discord and to edit it.

Commands: 

```
/plex invite <email>
This command is used to add an email to plex
/plex remove <email>
This command is used to remove an email from plex
/emby invite <emby username>
This command is used to add a user to Emby.
/emby remove <emby username>
This command is used to remove a user from Emby.
/membarr dbls
This command is used to list Membarr's database
/membarr dbadd <@user> <optional: plex email> <optional: emby username>
This command is used to add exsisting  plex emails, emby users and discord id to the DB.
/membarr dbrm <position>
This command is used to remove a record from the Db. Use /membarr dbls to determine record position. ex: /membarr dbrm 1
```
# Creating Discord Bot
1. Create the discord server that your users will get member roles or use an existing discord that you can assign roles from
2. Log into https://discord.com/developers/applications and click 'New Application'
3. (Optional) Add a short description and an icon for the bot. Save changes.
4. Go to 'Bot' section in the side menu
5. Uncheck 'Public Bot' under Authorization Flow
6. Check all 3 boxes under Privileged Gateway Intents: Presence Intent, Server Members Intent, Message Content Intent. Save changes.
7. Copy the token under the username or reset it to copy. This is the token used in the docker image.
8. Go to 'OAuth2' section in the side menu, then 'URL Generator'
9. Under Scopes, check 'bot' and applications.commands
10. Copy the 'Generated URL' and paste into your browser and add it to your discord server from Step 1.
11. The bot will come online after the docker container is running with the correct Bot Token


# Unraid Installation
> For Manual an Docker setup, see below

1. Ensure you have the Community Applications plugin installed.
2. Inside the Community Applications app store, search for Membarr.
3. Click the Install Button.
4. Add discord bot token.
5. Click apply
6. Finish setting up using [Setup Commands](#after-bot-has-started)

# Manual Setup (For Docker, see below)

**1. Enter discord bot token in bot.env**

**2. Install requirements**

```
pip3 install -r requirements.txt 
```
**3. Start the bot**
```
python3 Run.py
```

# Docker Setup & Start
To run Membarr in Docker, run the following command, replacing [path to config] with the absolute path to your bot config folder:
```
docker run -d --restart unless-stopped --name membarr -v /[path to config]:/app/app/config -e "token=YOUR_DISCORD_TOKEN_HERE" yoruio/membarr:latest
```

# After bot has started 

# Plex Setup Commands: 

```
/plexsettings setup <username> <password> <server name>
This command is used to setup plex login. 
/plexsettings addrole <@role>
These role(s) will be used as the role(s) to automatically invite user to plex
/plexsettings removerole <@role>
This command is used to remove a role that is being used to automatically invite uses to plex
/plexsettings setuplibs <libraries>
This command is used to setup plex libraries. Default is set to all. Libraries is a comma separated list.
/plexsettings enable
This command enables the Plex integration (currently only enables auto-add / auto-remove)
/plexsettings disable
This command disables the Plex integration (currently only disables auto-add / auto-remove)
```

# Emby Setup Commands:
```
/embysettings setup <server url> <api key> <optional: external server url (default: server url)>
This command is used to setup the Emby server. The external server URL is the URL that is sent to users to log into your Emby server.
/embysettings addrole <@role>
These role(s) will be used as the role(s) to automatically invite user to Emby
/embysettings removerole <@role>
This command is used to remove a role that is being used to automatically invite uses to Emby
/embysettings setuplibs <libraries>
This command is used to setup Emby libraries. Default is set to all. Libraries is a comma separated list.
/embysettings enable
This command enables the Emby integration (currently only enables auto-add / auto-remove)
/embysettings disable
This command disables the Emby integration (currently only disables auto-add / auto-remove)
```



# Other stuff
**Enable Intents else bot will not Dm users after they get the role.**
https://discordpy.readthedocs.io/en/latest/intents.html#privileged-intents
**Discord Bot requires Bot and application.commands permission to fully function.**
