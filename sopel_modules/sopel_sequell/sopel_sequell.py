# coding=utf-8

from sopel import module
from sopel.config.types import (
    StaticSection, ValidatedAttribute
)
from sopel.tools import get_logger

sequell_rule = r'^\$sq\$(.*)$'
logger = get_logger(__name__)

class SequellSection(StaticSection):
    relay_prefix = ValidatedAttribute('relay_prefix')
    relay_nick = ValidatedAttribute('relay_nick')
    relay_chan = ValidatedAttribute('relay_chan')


def configure(config):
    config.define_section('sequell', SequellSection)
    config.sequell.configure_setting(
        'relay_prefix',
        'Prefix for commands to relay (will be stripped)'
    )
    config.sequell.configure_setting(
        'relay_nick',
        'Nick for sequell the actual bot'
    )
    config.sequell.configure_setting(
        'relay_chan',
        'Channel for botspam (sequell replies)'
    )


def setup(bot):
    bot.config.define_section('sequell', SequellSection)
    sequell_rule = rf"^{bot.config.sequell.relay_prefix}(.*)$"


# Match all messages except for those which start with common bot command
# prefixes
@module.rule(sequell_rule)
def sequell_cmd(bot, trigger):
    logger.info(f"{trigger.nick} sent cmd {trigger.match.group(1)}")
    bot.say(f"{trigger.match.group(1)}", bot.config.sequell.relay_nick)


@module.require_privmsg
@module.rule(r'.*')
def sequell_reply(bot, trigger):
    logger.info(f"got a pm from {trigger.nick}")
    if trigger.nick == bot.config.sequell.relay_nick:
        logger.info(f"{trigger.nick} replied {trigger.match.string}")
        bot.say(trigger.match.string, bot.config.sequell.relay_chan)
