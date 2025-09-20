import discord
from discord import app_commands

with open('token.txt', 'r') as file:
    TOKEN = file.read()
MY_GUILD = discord.Object(id=1020417118610669680)


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.activity = discord.CustomActivity(name = "KILLING AND FUCKING")

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


class User:
    def __init__(self, uid):
        self.uid = uid
        self.alive = True
        self.alert_ready = True
        self.is_protected = False
        self.is_alerting = False
        self.target = None
        self.attackers = []
        """A list of User objects"""

UserList = {}

def get_user(uid):
    if uid not in UserList:
        UserList[uid] = User(uid)
        print(f'Added user {uid}')
    return UserList[uid]

def print_self_info(uid):
    u = get_user(uid)
    print(f'Alive: {u.alive} \nHas alert?: {u.alert_ready}')

def got_killed(user):
    user.alive = False
    if user.target:
        user.target.attackers.remove(user)
        user.target = None
    user.alert_ready = False


#not sure why these are separate but this is how i've seen it done so uhh
default_intents = discord.Intents.default()
client = MyClient(intents=default_intents)

@client.tree.command()
async def run_turn(interaction: discord.Interaction):
    kill_list = []
    output = ""
    for user in UserList:
        #this kinda sucks
        user = UserList[user]
        if user.is_alerting:
            user.alert_ready = False
            for attacker in user.attackers:
                kill_list.append(attacker)
                output += f'<@{attacker.uid}> was KILLed while trying to KILL someone\n'
            user.is_alerting = False
        elif not user.is_protected and user.attackers:
            kill_list.append(user)
            output += f'<@{user.uid}> got KILLed\n'

    await interaction.response.send_message(output)

    #Have to do this so you can kill and be killed in the same turn
    for user in kill_list:
        got_killed(user)

@client.tree.command()
@app_commands.describe(target='Who you want to KILL')
async def kill(interaction: discord.Interaction, target: discord.Member):
    """KILL someone"""
    user = get_user(interaction.user.id)
    target_user = get_user(target.id)

    if user.target is not None:
        user.target.attackers.remove(user)

    if user.alive:
        if target_user.alive:
            user.target = target_user
            target_user.attackers.append(user)

            await interaction.response.send_message(f'Ok, you\'re scheduled to KILL {target.mention} tonight',
                                                    ephemeral = True)
        else:
            await interaction.response.send_message(f'{target.mention} has already been KILLed, sorry!', ephemeral=True)
    else:
        await interaction.response.send_message(f'Sorry, you can\'t KILL anybody if you\'ve been KILLed!',
                                                ephemeral=True)

@client.tree.command()
async def alert(interaction: discord.Interaction):
    """Go on alert, KILLing anybody who tries to KILL you. You can only do this once."""
    user = get_user(interaction.user.id)
    if user.alert_ready:
        user.is_alerting = True
        await interaction.response.send_message(f'Ok, tonight you\'ll KILL anybody who tries to KILL you.',
                                                ephemeral = True)
    else:
        await interaction.response.send_message(f'Sorry, you\'ve already used your alert!.', ephemeral=True)

"""
@client.tree.command()
@app_commands.describe(target='Who you want to protect')
async def protect(interaction: discord.Interaction, target: discord.Member):
"""

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('----------------------------------------------')
    await client.tree.sync(guild=MY_GUILD)

@client.tree.command()
async def meow(interaction: discord.Interaction):
    await interaction.response.send_message('suck my nuts and lick on my shaft', ephemeral = True)

@client.tree.command()
async def status(interaction: discord.Interaction):
    user = get_user(interaction.user.id)
    if user.alive:
        output = 'You have NOT been KILLed (yet!)\n'
    else:
        output = 'You have been KILLed. Sorry!\n'
    if user.alert_ready:
        output += 'Your alert is still available\n'
    if user.target:
        output += f'You are going to (try to) KILL <@{user.target.uid}> tonight.'

    await interaction.response.send_message(output, ephemeral = True)

@client.tree.command()
async def reset(interaction: discord.Interaction):
    UserList.clear()
    await interaction.response.send_message('Data has been cleared', ephemeral=True)



client.run(TOKEN)