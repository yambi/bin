#!/bin/sh
keychain
COMMAND="ssh cherry -R 10022":localhost:22
pgrep -f -x "$COMMAND" > /dev/null 2>&1 || $COMMAND

