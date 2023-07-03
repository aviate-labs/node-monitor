spimport discord

class DiscordBot(discord.Client):
    async def on_ready(self):
        print(f'Logged on to discord as {self.user}!')

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return
        
        if message.content.startswith("$list"):
            await message.channel.send("nothing to list")

        elif message.content.startswith("$ping"):
            await message.channel.send("pong")


def run_bot(token):
    intents = discord.Intents.default()
    intents.message_content = True
    discordbot = DiscordBot(intents=intents)
    discordbot.run(token)






