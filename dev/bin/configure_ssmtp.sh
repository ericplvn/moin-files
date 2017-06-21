#!/bin/bash

if [ "$EUID" != "0" ]; then
    echo "Run as root"
    exit 1
fi

if [ -z "$AWS_ACCESS_KEY_ID" ]; then
    echo "Export AWS_ACCESS_KEY_ID"
    exit 1
fi

if [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "Export AWS_SECRET_ACCESS_KEY"
    exit 1
fi

USER=mike
DOMAIN=crute.us
SERVER=email-smtp.us-west-2.amazonaws.com:587

cat > /etc/ssmtp/ssmtp.conf <<EOF
#
# Config file for sSMTP sendmail
#
# The person who gets all mail for userids < 1000
# Make this empty to disable rewriting.
root=$USER@$DOMAIN

# The place where the mail goes. The actual machine name is required no 
# MX records are consulted. Commonly mailhosts are named mail.domain.com
mailhub=$SERVER

# Where will the mail seem to come from?
rewriteDomain=crute.us

# The full hostname
hostname=$(hostname -f)

# Use SSL/TLS before starting negotiation
UseTLS=Yes
UseSTARTTLS=Yes

# Username/Password
AuthUser=$AWS_ACCESS_KEY_ID
AuthPass=$(/usr/bin/ses_password_convert.py $AWS_SECRET_ACCESS_KEY)

# Are users allowed to set their own From: address?
# YES - Allow the user to specify their own From: address
# NO - Use the system generated From: address
FromLineOverride=YES
EOF
