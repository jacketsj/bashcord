import subprocess
import discord
import asyncio
import argparse
import json
from discord.ext import commands

# Function to load configuration from a JSON file
def load_config(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)

# Initialize the Discord bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

async def send_output_to_discord(target, output, file_paths):
    # Determine the destination (user or channel) for the message
    if isinstance(target, discord.User) or isinstance(target, discord.Member):
        destination = target
    elif isinstance(target, discord.TextChannel):
        destination = target
    else:
        raise ValueError("Invalid target for message.")

    # Send the output as a text file
    with open('/tmp/output.txt', 'w') as file:
        file.write(output)
    with open('/tmp/output.txt', 'rb') as file:
        await destination.send(file=discord.File(file, 'output.txt'))

    # Send the specified files
    for file_path in file_paths:
        with open(file_path, 'rb') as file:
            await destination.send(file=discord.File(file))

# Parse arguments from command line
parser = argparse.ArgumentParser(description="Run a bash command and send output to Discord.")
parser.add_argument('command', type=str, help='The bash command to run')
parser.add_argument('--lines', type=int, help='Number of lines from the end of output to send')
parser.add_argument('--files', nargs='*', help='Paths to files to send', default=[])
parser.add_argument('--user', type=int, help='Discord user ID to send the message to', default=None)
parser.add_argument('--channel', type=int, help='Discord channel ID to send the message to', default=None)
parser.add_argument('--config', type=str, help='Path to JSON configuration file', default='default_config.json')
parser.add_argument('--token', type=str, help='Discord bot token', default=None)
args = parser.parse_args()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

    # Load configuration file
    config = load_config(args.config)

    # Override defaults with command-line arguments
    token = args.token if args.token else config['Discord']['Token']
    lines = args.lines if args.lines is not None else config['Defaults']['Lines']
    user_id = args.user if args.user else config['Defaults'].get('User')
    channel_id = args.channel if args.channel else config['Defaults'].get('Channel')

    # Execute the bash command
    with open('/tmp/output.txt', 'w') as file:
        process = subprocess.Popen(args.command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Read the output line by line and write to terminal and file
        for line in iter(process.stdout.readline, ''):
            print(line, end='')  # Print to terminal
            file.write(line)     # Write to file

    # Determine the target (user or channel) to send the message to
    if user_id:
        target = await bot.fetch_user(user_id)
    elif channel_id:
        target = bot.get_channel(channel_id)
    else:
        print("No valid user or channel specified.")
        await bot.close()
        return

    # Read the last N lines from the file
    with open('/tmp/output.txt', 'r') as file:
        output_lines = file.readlines()
    last_lines = ''.join(output_lines[-lines:])

    # Send the output and files to Discord
    await send_output_to_discord(target, last_lines, args.files)

    # Close the bot after sending the message
    await bot.close()

# Run the bot
bot.run(load_config(args.config)['Discord']['Token'] if args.token is None else args.token)
