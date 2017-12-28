FROM alpine:3.7

RUN apk add --update --no-cache \
	    ncftp \
	    pwgen \
	    rsync \
	    openssh-client \
	    duply \
	    gnupg \
	    py-pip && pip install \
	    fasteners \
	    dropbox==6.9.0 \
	    boto


COPY conf /etc/duply
RUN chmod -R 700 /etc/duply

CMD /bin/bash
