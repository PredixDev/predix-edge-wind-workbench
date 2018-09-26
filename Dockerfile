FROM registry.gear.ge.com/predix_edge/pycdp-dev-amd64:1.0

ENV LANG C.UTF-8

RUN echo @testing apk add --upgrade apk-tools@edge

RUN echo @testing http://dl-cdn.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories \
    && apk add --update --no-cache \
        curl \
        g++ \
        pkgconfig \
        freetype-dev \
        py-numpy-dev@testing \
        wget

RUN echo @testing apk add --update --no-cache \
    && apk add --update py-pip \
    && pip install --upgrade pip \
    && pip install --no-cache-dir setuptools numpy matplotlib scipy \
    && find /usr/local -depth \
        \( \
            \( -type d -a -name test -o -name tests \) \
            -o \
            \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        \) -exec rm -rf '{}' + \
    && apk add --virtual .python-deps \
        python \
        py-numpy \
        freetype \
        libpng \
        nano \
    && apk del \
        curl \
        g++ \
        gcc \
        pkgconfig \
        libc-dev \
        ncurses-dev \
        openssl-dev \
        zlib-dev \
        libpng-dev \
        freetype-dev \
        python-dev \
        cython-dev \
        py-numpy-dev \
    && rm -rf /usr/src/python ~/.cache

ADD ./src/models/image_contents.tar.gz /

COPY ./src/models /opt/microservice

COPY ./src/server /opt/server

COPY ./src/requirements.txt /opt

WORKDIR /opt

RUN pip install -U pip setuptools \
    && pip install -r requirements.txt


COPY ./src/entry_point.sh /

WORKDIR /
RUN chmod +x entry_point.sh
ENV PYTHONPATH=$PYTHONPATH:/usr/local/lib/python2.7/site-packages

EXPOSE 9005
ENTRYPOINT ["/entry_point.sh"]
