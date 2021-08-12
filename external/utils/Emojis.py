#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/1/2 13:28
# @File    : Emojis.py
import emoji
emojis = \
    '😀😁😂🤣😃😄😅😆😉😊😋😎😍😘😗😙😚🙂🤗🤔😐😑😶🙄😏😣😥😮🤐😯' \
    '😪😫😴😌🤓😛😜😝🤤😒😓😔😕🙃🤑😲😇🤠🤡🤥😺😸😹😻😼😽🙀😿😾🙈' \
    '🙉🙊🌱🌲🌳🌴🌵🌾🌿🍀🍁🍂🍃🍇🍈🍉🍊🍋🍌🍍🍏🍐🍑🍒🍓🥝🍅🥑🍆🥔' \
    '🥕🌽🥒🍄🥜🌰🍞🥐🥖🥞🧀🍖🍗🥓🍔🍟🍕🌭🌮🌯🥙🥚🍳🥘🍲🥗🍿🍱🍘🍙' \
    '🍚🍛🍜🍝🍠🍢🍣🍤🍥🍡🍦🍧🍨🍩🍪🎂🍰🍫🍬🍭🍮🍯🍼🥛☕🍵🍶🍾🍷🍸' \
    '🍹🍺🍻🥂🥃🍴🥄🔪🏺🌍🌎🌏🌐🗾🌋🗻🏠🏡🏢🏣🏤🏥🏦🏨🏩🏪🏫🏬🏭🏯' \
    '🏰💒🗼🗽⛪🕌🕍🕋⛲⛺🌁🌃🌄🌅🌆🌇🌉🌌🎠🎡🎢💈🎪🎭🎨🎰🚂🚃🚄🚅' \
    '🚆🚇🚈🚉🚊🚝🚞🚋🚌🚍🚎🚐🚑🚒🚓🚔🚕🚖🚗🚘🚙🚚🚛🚜🚲🛴🛵🚏⛽🚨' \
    '🚥🚦🚧⚓⛵🛶🚤🚢🛫🛬💺🚁🚟🚠🚡🚀🚪🛌🚽🚿🛀🛁⌛⏳⌚⏰🌑🌒🌓🌔' \
    '🌕🌖🌗🌘🌙🌚🌛🌜🌝🌞⭐🌟🌠⛅🌀🌈🌂☔⚡⛄🔥💧🌊🎃🎄🎆🎇✨🎈🎉' \
    '🎊🎋🎍🎎🎏🎐🎑🎁🎫🏆🏅🥇🥈🥉⚽⚾🏀🏐🏈🏉🎾🎱🎳🏏🏑🏒🏓🏸🥊🥋' \
    '🥅🎯⛳🎣🎽🎿🎮🎲🃏🎴🔇🔈🔉🔊📢📣📯🔔🔕🎼🎵🎶🎤🎧📻🎷🎸🎹🎺🎻' \
    '🥁📱📲📞📟📠🔋🔌💻💽💾💿📀🎥🎬📺📷📸📹📼🔍🔎🔬🔭📡💡🔦📔📕📖' \
    '📗📘📙📚📓📒📃📜📄📰📑🔖💰💴💵💶💷💸💳💱💲📧📨📩📤📥📦📫📪📬' \
    '📭📮📝💼📁📂📅📆📇📋📌📍📎📏📐🔒🔓🔏🔐🔑🔨🔫🏹🔧🔩🔗🚬🗿🔮🛒'

if __name__ == '__main__':
    print(emoji.emojize('你的提醒都在这里啦 :facepunch:',use_aliases=True))