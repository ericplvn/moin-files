FROM ubuntu:14.04
MAINTAINER Eric Levine <ericplvn@msn.com>

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y curl ssmtp python-pip python-xapian wamerican fckeditor uwsgi uwsgi-plugin-python python-imaging emacs tmux && \
    pip install moin markdown docutils textile pygments && \
    useradd -r -M -d /srv/wiki -s /bin/nologin wiki

ADD entrypoint.sh /entrypoint.sh
ADD bin/* /usr/bin/

RUN \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*

STOPSIGNAL SIGINT
VOLUME "/srv/wiki"
ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["/usr/bin/uwsgi", "--ini", "/srv/wiki/config/uwsgi.ini"]
