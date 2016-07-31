"""
User commands definition
========================

Must be like the following example::

    USER_COMMANDS = (
        (<command_1_code>, <command_N_title>),
        ...
        (<command_N_code>, <command_N_title>),
    )

Codes 0..99 - reserved. Do not use them.
"""


USER_CODE1 = 100
USER_CODE2 = 110

USER_COMMANDS = (
    (USER_CODE1, 'Custom command #1'),
    (USER_CODE2, 'Custom command #2'),
)
