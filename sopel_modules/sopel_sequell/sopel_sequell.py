# coding=utf-8

import re
from sopel import plugin
from sopel.config.types import (
    StaticSection, ValidatedAttribute, ListAttribute
)
from sopel.tools import get_logger

PLUGIN_CMD = 'sq'
ADD_NICK_CMDS = [
    'dump',
    'lg',
    'gamesby',
]
LOGGER = get_logger(__name__)


class SequellSection(StaticSection):
    nick = ValidatedAttribute('nick')
    chans = ListAttribute('chans')


def configure(config):
    config.define_section('sequell', SequellSection)
    config.sequell.configure_setting(
        'nick',
        'Nick for Sequell the actual bot',
    )
    config.sequell.configure_setting(
        'chans',
        'Channels with allowed botspam',
    )


def setup(bot):
    bot.config.define_section('sequell', SequellSection)
    bot.config.sequell.chans = [item for a in bot.config.sequell.chans for item in a.split(",")]
    LOGGER.debug(f"Sequel relay configured for channels: {bot.config.sequell.chans}")
    bot.memory['sequell_sender'] = bot.config.sequell.chans[0]


def parse(cmd):
    match = re.compile(r"""^
    ([!?&][?@]*)    # sequell prefix
    (\w+)           # sequell cmd
    (?:\[.*\])?     # optional with ?? cmds
    (?:\s+
      ([^\s]+)      # trailing params
    )*
$""", re.X).match(cmd)
    if match is None:
        return None, None, None
    LOGGER.debug(f"{match.group(1)}, {match.group(2)}, {match.group(3)}")
    return match.group(1), match.group(2), match.group(3)


def relay_cmd(bot, cmd_full, nick, recv_bot):
    prefix, cmd, params = parse(cmd_full)
    if prefix not in ("??", "??@") and cmd in ADD_NICK_CMDS and params is None:
        cmd_full += f" {nick}"
    bot.say(cmd_full, recv_bot)


def sequell(bot, trigger, cmd):
    if trigger.sender.is_nick() or trigger.sender in bot.config.sequell.chans:
        bot.memory['sequell_sender'] = trigger.sender
        relay_cmd(
            bot,
            cmd,
            trigger.nick,
            bot.config.sequell.nick
        )


@plugin.command(PLUGIN_CMD)
def sequell_command(bot, trigger):
    # matches g1 (.sq) g2 (the rest), trim our plugin_cmd
    LOGGER.debug(f"<{trigger.nick}> (CMD) {trigger.match.string}")
    sequell(bot, trigger, trigger.match.group(2))


@plugin.rule(r'^[!\?&][@\?]*')
def sequell_rule(bot, trigger):
    # in this case we relay the whole thing
    LOGGER.debug(f"<{trigger.nick}> (RULE) {trigger.match.string}")
    sequell(bot, trigger, trigger.match.string)


@plugin.require_privmsg
@plugin.rule(r'.*')
def sequell_reply(bot, trigger):
    if trigger.nick == bot.config.sequell.nick:
        bot.say(trigger.match.string, bot.memory['sequell_sender'])
