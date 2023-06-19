import discord, time, json, poe, random
import aiohttp
from discord import app_commands
from discord.ext import commands
import asyncio

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

token = config['token']

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all(), proxy="http://127.0.0.1:7890")

models = {
    'claude-v1': 'a2_2',
    'claude-instant': 'a2',
    'claude-instant-100k': 'a2_100k',
    'sage': 'capybara',
    'gpt-4': 'beaver',
    'gpt-3.5-turbo': 'chinchilla',
}


@bot.event
async def on_ready():
    print(f"{bot.user} aka {bot.user.name} has connected to Discord!")

    invite_link = discord.utils.oauth_url(
        bot.user.id,
        permissions=discord.Permissions(),
        scopes=("bot", "applications.commands")
    )
    synced = await bot.tree.sync()
    print(f'Synced {len(synced)} commands.')
    print(f"\n\nInvite your Discrd bot using the following invite: {invite_link}\n\n")


@bot.command(name='test', description='ping the bot')
async def test(interaction: discord.Interaction):
    print(interaction.message.attachments[0].url)

    interaction.response.send_message('pong')


@bot.tree.command(name='help', description='Help, and available language-models')
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title='g4f.ai help',
                          description='available models:\n```asm\ngpt-4\ngpt-3.5-turbo\nclaude-v1\nclaude-instant\nclaude-instant-100k\n```\ncommands:\n```asm\n/help\n/create <prompt> <model (default: gpt-4)>\n```',
                          color=8716543)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name='create', description='prompt a language model (gpt-4, claude etc...)')
@app_commands.describe(prompt='prompt', model='model')
async def say(interaction: discord.Interaction, prompt: str, model: str = 'gpt-4'):
    try:

        print(interaction.user.name, prompt, model)
        await interaction.response.defer(ephemeral=False, thinking=True)
        base = f'*model*: `{model}`\n'
        system = 'system: your response will be rendered in a discord message, include language hints when returning code like: ```py ...```, and use * or ** or > to create highlights ||\n prompt: '

        flag = False
        client = None
        flagNum = 0
        token = None
        while flagNum <= 10:
            print("Attempting poe token...")
            try:
                flagNum += 1
                token = random.choice(open('tokens.txt', 'r').read().splitlines())
                client = poe.Client(token.split(':')[0], proxy="http://127.0.0.1:7890")

                print("token.split(':')[0]:", token.split(':')[0])

                # await interaction.response.send_message(base)
                base += '\n'

                completion = client.send_message(models[model],
                                                 system + prompt, with_chat_break=True)

                print("remaining message：", client.get_remaining_messages(models[model]))
                if client.get_remaining_messages(models[model]) == None or client.get_remaining_messages(
                        models[model]) == 0:
                    continue

                await interaction.followup.send(base)

                for token in completion:
                    print("token", token)
                    base += token['text_new']
                    base = base.replace('Discord Message:', '')
                    await interaction.edit_original_response(content=base)

                break
            except Exception as e:
                print("invalid token，Attempting other token", "exception code：", e)
                traceback.print_exc()
            else:
                break
        if flagNum > 10:
            print("suggest change token list")




    except Exception as e:
        await interaction.response.send_message(f'an error occured: {e}')


bot.run(token)
