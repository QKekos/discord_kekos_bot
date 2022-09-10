
import re
import discord
import config


class BotClient(discord.Client):
    async def on_message(self, message):
        if not message.content.startswith(config.PREFIX):
            return

        command = self.get_command(config.PREFIX, message)

        if command == 'color':
            await self.set_color(message)

        else:
            await message.channel.send('Invalid command!')

    async def set_color(self, message):
        if len(message.content.split(' ')) != 2:
            return await message.channel.send('Invalid color parameters!')

        color = await self.get_color(message)

        if not isinstance(color, int):
            return

        single_roles = self.get_single_roles(message)

        if not single_roles:
            return await message.channel.send('You have no unique roles!')

        single_roles = [role for role in single_roles if len(role.name.split(' ')) >= config.min_words]

        if not single_roles:
            return await message.channel.send(f'You have no unique roles with more than {config.min_words} words')

        role = single_roles[0]
        await role.edit(color=color)

    @staticmethod
    def get_command(prefix, message):
        return re.findall(f'{prefix}(\w+)', message.content)[0]

    @staticmethod
    async def get_color(message):
        color = message.content.split(' ')[-1]

        try:
            return int(color.capitalize(), 16)

        except ValueError:
            return await message.channel.send(f'{color} is invalid color! Color must be hex')

    @staticmethod
    def get_single_roles(message):
        return [
            role for role in message.author.roles if sum([
                1 for memeber in message.guild.members if role in memeber.roles
            ]) == 1
        ]


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = BotClient(intents=intents)
client.run(config.TOKEN)
