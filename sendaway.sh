#!/bin/ksh

EMAIL=${1:?Enter address}
SUBJECT=${2:?Enter subject}
MESSAGE=${3:?Enter message}
ATTACH=${4}

export TERM=xterm
expect >/dev/null <<EOF
set timeout 120
spawn alpine "$EMAIL"
expect "To AddrBk"
send "$SUBJECT$ATTACH\r\r$MESSAGE\rY"
expect "Alpine finished"
EOF
