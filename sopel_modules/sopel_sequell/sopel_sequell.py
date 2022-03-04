# coding=utf-8

import re
from sopel import plugin
from sopel.config.types import (
    StaticSection, ValidatedAttribute
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
    sq_nick = ValidatedAttribute('sq_nick')
    to_chan = ValidatedAttribute('to_chan')


def configure(config):
    config.define_section('sequell', SequellSection)
    config.sequell.configure_setting(
        'sq_nick',
        'Nick for Sequell the actual bot',
    )
    config.sequell.configure_setting(
        'to_chan',
        'Channel for botspam (sequell replies)',
    )


def setup(bot):
    bot.config.define_section('sequell', SequellSection)
    bot.memory['sequell'] = {}


def parse(cmd):
    match = re.compile(r"""^
    ([!\?&][\?@]*)     # sequell prefix
    (\w+)              # sequell cmd
    (?:\[.*\])         # optional with ?? cmds
    (?:\s+
      ([^\s]+)         # trailing params
    )*
$""", re.X).match(cmd)
    if match is None:
        return None, None, None
    return match.group(1), match.group(2), match.group(3)


def relay_cmd(bot, cmd_full, sender, pm, recv_bot):
    prefix, cmd, params = parse(cmd_full)

    bot.memory['sequell'] = {
        'from': sender,
        'pm': pm,
    }

    if prefix not in ("??", "??@") and cmd in ADD_NICK_CMDS and params is None:
        cmd_full += f" {sender}"
    bot.say(cmd_full, recv_bot)


def sequell(bot, trigger, cmd):
    relay_cmd(
        bot,
        cmd,
        trigger.nick,
        trigger.is_privmsg,
        bot.config.sequell.sq_nick
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
    if trigger.nick == bot.config.sequell.sq_nick:
        last_cmd = bot.memory['sequell']
        send_to = bot.config.sequell.to_chan
        if last_cmd['pm']:
            send_to = last_cmd['from']
        bot.say(trigger.match.string, send_to)
