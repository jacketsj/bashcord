# Bashcord
I got tired of waiting to come home to check the output of jobs run on my home computer, so now I send the results to myself over discord.

Example usage:
1. Add your bot token and channel/user id to `example_config.json`
2. Install the necessary packages:
```sh
pip install -r requirements.txt
```
2. Execute a command:
```sh
python3 bashcord.py "echo 'hello world'" --lines 10 --config example_config.json
python3 bashcord.py "echo 'hello world'" --lines 10 --config example_config.json --files file1.png file2.png
```
