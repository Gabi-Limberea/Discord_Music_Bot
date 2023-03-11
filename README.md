# Discord music bot

## Basic description:

This is a music bot for discord. It started out as a college assignment, but I
have decided to continue working on it and make it a real project. It is in
early development, so it is not very stable yet. It can play music from Youtube
or from a local library.

## Requirements:

* **Python 3.6** or higher
* **Pip** (for installing dependencies)
* **Venv** (for creating a virtual environment)
* **Direnv** (for loading environment variables from .envrc)
* *Optional:* 
  * **Docker** (for running the bot in a container)

You also need a .envrc file in the root directory of the project. It should
contain the following variables:

```bash
    export BOT_TOKEN="your bot token"
```

## Installation:

1. Clone the repository using `git clone`
2. Create a virtual environment and install requirements using 
`make install-reqs`
3. Run the bot:
   1. **Locally**: `make run`
   2. **In a container**: `make docker-run`

## Usage:

The bot has a few commands. You can see them by typing `!help` in a channel
where the bot is present. The bot's prefix is `!`.

## Plans for the future:

* Add queueing system for songs
* Refactor the code to make it more readable
* Deploy the bot to a Kubernetes cluster
* Finish the secrets feature, so that the bot can tell secrets to users and 
remember secrets told by users (gimmick feature)