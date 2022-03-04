# coding=utf-8

import re
from sopel import plugin
from sopel.config.types import (
    StaticSection, ValidatedAttribute
)
from sopel.tools import get_logger

cmd = 'sq'
nick_sub_cmd_list = [
    'dump',
    'lg',
    'gamesby',
]
logger = get_logger(__name__)

class SequellSection(StaticSection):
    cmd = ValidatedAttribute('cmd')
    sq_nick = ValidatedAttribute('sq_nick')
    to_chan = ValidatedAttribute('to_chan')


def configure(config):
    config.define_section('sequell', SequellSection)
    config.sequell.configure_setting(
        'cmd',
        'Name of Sequell relay command (default: sq)'
    )
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
    if bot.config.sequell.cmd is not None:
         cmd = bot.config.sequell.cmd
    bot.memory['sequell'] = []


# Match all messages except for those which start with common bot command
# prefixes
@plugin.command(cmd)
def sequell_cmd(bot, trigger):
    pattern = re.compile(r"""^
    ([&!\?]+)   # sequell prefix
    (\w+)       # sequell cmd
    (?:\s+
      (\w+)     # trailing parameters
    )*
$""", re.X)
    logger.debug(f"<{trigger.nick}> {trigger.match.string}")
    match = pattern.match(trigger.match.group(2))
    if match is None:
        return
    cmd = match.group(2)
    params = match.group(3)
    bot.memory['sequell'].append({
        'from': trigger.nick,
        'pm': trigger.is_privmsg
    })
    logger.debug(f"cmd matched: {match.group(1)}, {cmd}, {params}")
    msg = f"{match.group(0)}"
    if cmd in nick_sub_cmd_list and params is None:
        msg += f" {trigger.nick}"
    bot.say(msg, bot.config.sequell.sq_nick)


@plugin.require_privmsg
@plugin.rule(r'.*')
def sequell_reply(bot, trigger):
    if trigger.nick == bot.config.sequell.sq_nick:
        logger.info(f"{trigger.nick} replied {trigger.match.string}")
        last_cmd = bot.memory['sequell'].pop(-1)
        if last_cmd['pm']:
            bot.say(trigger.match.string, last_cmd['from'])
        else:
            bot.say(trigger.match.string, bot.config.sequell.to_chan)
