FROM fedora:28

# Env variable USER specific the kebechet as committer while git branch and git commit creation. 
ENV USER=kebechet \
    PIPENV_CACHE_DIR=/home/user \
    LC_ALL=en_US.UTF-8 \
    LANG=en_US.UTF-8

# Add the ssh key from local dir to container dir.
# ADD github /home/user/.ssh/id_rsa

RUN \
    dnf install -y --setopt=tsflags=nodocs git python3-pip gcc redhat-rpm-config python3-devel which &&\
    pip3 install kebechet &&\
    mkdir /home/user /home/user/.ssh &&\
    chmod a+wr /etc/passwd /home/user

COPY docker-entrypoint.sh /

# Arbitrary User
USER 1042 
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["run"]
