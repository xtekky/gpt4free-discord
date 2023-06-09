
import discord, time, json, poe, random

from discord import app_commands
from discord.ext import commands

token = json.loads(open('config.json', 'r').read())['token']
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

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
    synced = await bot.tree.sync()
    print(f'Synced {len(synced)} commands.')
    
@bot.command(name='test', description='ping the bot')
async def test(interaction: discord.Interaction):
    print(interaction.message.attachments[0].url)
    
    interaction.response.send_message('pong')
    
@bot.tree.command(name='help', description='Help, and available language-models')
async def help(interaction: discord.Interaction):
    
    embed = discord.Embed( title='g4f.ai help', 
        description='available models:\n```asm\ngpt-4\ngpt-3.5-turbo\nclaude-v1\nclaude-instant\nclaude-instant-100k\n```\ncommands:\n```asm\n/help\n/create <prompt> <model (default: gpt-4)>\n```',
        color=8716543)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='create', description='prompt a language model (gpt-4, claude etc...)')
@app_commands.describe(prompt='prompt', model='model')
async def say(interaction: discord.Interaction, prompt: str, model: str = 'gpt-4'):
    try:
        print(interaction.user.name, prompt, model)
        
        base = f'*model*: `{model}`\n'
        system = 'system: your response will be rendered in a discord message, include language hints when returning code like: ```py ...```, and use * or ** or > to create highlights ||\n prompt: '
        
        token = random.choice(open('tokens.txt', 'r').read().splitlines())
        client = poe.Client(token.split(':')[0])
        
        await interaction.response.send_message(base)
        base += '\n'
        
        completion = client.send_message(models[model],
                                        system + prompt, with_chat_break=True)
        
        for token in completion:
            base += token['text_new']
            
            base = base.replace('Discord Message:', '')
            await interaction.edit_original_response(content=base)
    
    except Exception as e:
        await interaction.response.send_message(f'an error occured: {e}')

bot.run(token)