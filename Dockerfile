FROM registry.access.redhat.com/ubi8

# Env variable USER specific the kebechet as committer while git branch and git commit creation. 
ENV USER=kebechet \
    PIPENV_CACHE_DIR=/home/user/.cache/pipenv \
    HOME=/home/user/ \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PYTHONPATH=.

WORKDIR /home/user

# Add the ssh key from local dir to container dir.
# ADD github /home/user/.ssh/id_rsa

RUN \
    dnf install -y --setopt=tsflags=nodocs git python3-pip gcc redhat-rpm-config python3-devel which gcc-c++ &&\
#    pip3 install git+https://github.com/thoth-station/kebechet &&\
    pip3 install pipenv &&\
    mkdir -p /home/user/.ssh &&\
    chmod a+wrx -R /etc/passwd /home/user

# For local installation from sources.
# ADD ./ /tmp/kebechet
# RUN  pip3 install virtualenv && mkdir -p /usr/local/lib/python3.6/site-packages/ && cd /tmp/kebechet/ && python3 setup.py install

COPY . /home/user
RUN pipenv install

# Arbitrary User
USER 1042 
CMD ["./app.sh"]
