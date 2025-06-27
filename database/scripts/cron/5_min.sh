#!/bin/sh

DBUSER=${DBUSER:-cron}
DBNAME=${DBNAME:-authentication-service}

psql -U ${DBUSER} -d ${DBNAME} -f "$(dirname "$0")/5_min.sql"
