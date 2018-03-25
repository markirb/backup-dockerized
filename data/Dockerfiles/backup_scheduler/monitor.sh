#!/bin/bash

if [[ "${USE_WATCHDOG}" =~ ^([nN][oO]|[nN])+$ ]]; then
  echo -e "$(date) - USE_WATCHDOG=n, skipping watchdog..."
  sleep 365d
  exec $(readlink -f "$0")
fi

trap "exit" INT TERM
trap "kill 0" EXIT

log_msg() {
  echo $(date) $(printf '%s\n' "${1}")
}

function mail_error() {
  [[ -z ${1} ]] && return 1
  [[ -z ${2} ]] && return 1
  RCPT_DOMAIN=$(echo ${1} | awk -F @ {'print $NF'})
  RCPT_MX=$(dig +short ${RCPT_DOMAIN} mx | sort -n | awk '{print $2; exit}')
  if [[ -z ${RCPT_MX} ]]; then
    log_msg "Cannot determine MX for ${1}, skipping email notification..."
    return 1
  fi
  ./smtp-cli --missing-modules-ok \
    --subject="Backup not functional" \
    --body-plain="${2}" \
    --to=${1} \
    --from="watchdog@${MAILCOW_HOSTNAME}" \
    --server="${RCPT_MX}" \
    --hello-host=${MAILCOW_HOSTNAME}
  log_msg "Sent notification email to ${1}"
}


while true; do
  BACKUP_PROFILES=($(/docker_backup.py list))
  msg_acc=""
  sts=0
  for profile in "${BACKUP_PROFILES[@]}";  do
    log_msg "Checking backup for $profile"  
    msg=$(./docker_backup.py $profile status | ./duply_check.py)
    sts=$sts+$?
    log_msg "${profile} backup ${msg}"
    msg_acc="${msg_acc}
${profile} backup: ${msg}"
  done
  if [[ $sts -gt 0 ]]; then
    [[ ! -z ${WATCHDOG_NOTIFY_EMAIL} ]] && mail_error "${WATCHDOG_NOTIFY_EMAIL}" "${msg_acc}"
  fi
  log_msg "Checked backup sleeping for another day"
  sleep 1d
done
