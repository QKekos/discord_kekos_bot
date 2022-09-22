
import re
import discord
import config


used_config = config.main


class BotClient(discord.Client):
    async def on_message(self, message: discord.Message):
        if not message.content.startswith(config.PREFIX):
            return

        command = self.get_command(config.PREFIX, message)  # !command arg -> command

        if not message.channel.id == used_config.get('chat_id'):
            return

        if command == 'color':
            await self.set_color(message)

        elif command == 'color_aliases':
            await self.write_aliases(message)

    async def set_color(self, message: discord.Message):
        if len(message.content.split(' ')) != 2:
            return await message.channel.send('Invalid color parameters!')

        try:
            color = await self.get_color(message)  # !color 00ff00 -> discord.Colour("#00ff00")

        except ValueError:
            return

        single_roles = self.get_single_roles(message)  # roles that only message author has

        if not single_roles:
            return await message.channel.send('You have no unique roles!')

        # Filter if single roles has >= config.min_words_in_role words in themselves
        single_roles = [role for role in single_roles if len(role.name.split(' ')) >= config.min_words_in_role]

        if not single_roles:
            return await message.channel.send(
                f'You have no unique roles with more than {config.min_words_in_role} words in it\'s name'
            )

        role = single_roles[0]
        await role.edit(color=color)

        await message.channel.send(
            f'Succesfully updated role "{role}" with color "{message.content.split(" ")[-1]}"!'
        )

    @staticmethod
    async def write_aliases(message: discord.Message):
        """
        Prints all aliases from config.aliases_to_print
        """
        await message.channel.send('\n'.join(config.aliases_to_print))

    @staticmethod
    def get_command(prefix: str, message: discord.Message) -> str:
        """
        {prefix}command ... -> command
        """

        return re.findall(f'{prefix}(\w+)', message.content)[0]  #

    @staticmethod
    async def get_color(message: discord.Message) -> discord.Colour:
        color = message.content.split(' ')[-1]

        if color.startswith('#'):
            color = color[1:]

        if hasattr(discord.Color, color):
            return getattr(discord.Color, color)()

        try:
            return discord.Color(int(color.capitalize(), 16))

        except ValueError:
            await message.channel.send(f'{color} is invalid color! Color must be hex')
            raise ValueError('Wrong color')

    @staticmethod
    def get_single_roles(message: discord.Message) -> [discord.Role]:
        return [
            role for role in message.author.roles if sum([
                1 for memeber in message.guild.members if role in memeber.roles
            ]) == 1
        ]


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = BotClient(intents=intents)
client.run(used_config.get('token'))
