FROM python:2-alpine

RUN apk add --update \
	&& apk add --no-cache curl \
	tzdata \
	bash \
	bind-tools \
	perl \
	perl-io-socket-ssl \
	perl-socket \
	perl-socket6 \
	perl-mime-lite \
	perl-term-readkey \
	tini \
	&& pip install docker pyyaml && curl https://raw.githubusercontent.com/mludvig/smtp-cli/v3.8/smtp-cli -o /smtp-cli \
	&& chmod +x smtp-cli

COPY monitor.sh /monitor.sh
COPY docker_backup.py /docker_backup.py
COPY duply_check.py /duply_check.py

COPY crontab /var/spool/cron/crontabs/root

COPY daily   /etc/periodic/daily/backup
RUN chmod +x /etc/periodic/daily/backup

COPY monthly /etc/periodic/monthly/backup
RUN chmod +x /etc/periodic/monthly/backup

ENTRYPOINT ["/sbin/tini", "-g", "--"]
# Less verbose
CMD /monitor.sh 2> /dev/null
