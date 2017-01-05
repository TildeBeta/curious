"""
The base class for a plugin.
"""
import typing

from curious.commands import bot as c_bot
from curious.commands.command import Command
from curious.commands.context import Context


class Plugin(object):
    def __init__(self, bot: 'c_bot.CommandsBot'):
        self.bot = bot

    @property
    def name(self):
        """
        Gets the name of this plugin.

        This is mostly for usage in subclasses to customize the name of the plugin from the default type name.
        """
        return self.__class__.__name__

    async def load(self):
        """
        Called just after the plugin has loaded, before any commands have been registered. Used for async loading.
        """

    async def unload(self):
        """
        Called just before the plugin is to be unloaded, after all commands have been removed.
        """

    async def plugin_check(self, ctx: Context):
        """
        Added as a check for every command in this plugin.
        """

    def _scan_body(self) -> typing.Tuple[list, list]:
        """
        Scans the body of this type for events and commands.

        :return: Two lists, the first one containing events and the second one containing commands.
        """
        events = []
        commands = []

        for name, value in self.__class__.__dict__.items():
            if hasattr(value, "factory"):
                # this is set by the decorator to create a new command instance
                cmd = value.factory()
                commands.append(cmd)

            elif hasattr(value, "event"):
                events.append(value)

        return events, commands

    @classmethod
    async def setup(cls, bot: 'c_bot.CommandsBot', *args, **kwargs):
        """
        Default setup function for a plugin.

        This will create a new instance of the class, then add it as a Plugin to the bot.
        """
        instance = cls(bot, *args, **kwargs)
        await instance.load()
        bot.add_plugin(instance)