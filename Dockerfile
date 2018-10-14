FROM dtr.predix.io/predix-edge/alpine-amd64

LABEL maintainer="Predix Builder Relations"
LABEL org="https://hub.docker.com/u/predixadoption"
LABEL version="1.0.29"
LABEL support="https://forum.predix.io"
LABEL license="https://github.com/PredixDev/predix-docker-samples/blob/master/LICENSE.md"

ENV LANG C.UTF-8

ENV CDP_VERSION 1.0.0

RUN echo @testing apk add --upgrade apk-tools@edge

RUN echo @testing http://dl-cdn.alpinelinux.org/alpine/edge/testing >> /etc/apk/repositories \
    && apk add --update --no-cache \
    curl \
    g++ \
    tar \
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

RUN pwd \
    && ls

COPY Packages.tar /tmp/Packages.tar

RUN apk add --update --virtual .build-deps \
    && tar -C /tmp -xvf /tmp/Packages.tar \
  	\
  	# Copy the current repositories file so that we can move it back later.
  	&& cp /etc/apk/repositories /etc/apk/old-repositories \
  	# Add the downloaded apk's to the list of repositories
  	&& echo "/tmp/Packages/internal" >> /etc/apk/repositories \
  	&& echo "/tmp/Packages/external" >> /etc/apk/repositories \
  	&& echo "/tmp/Packages/edge" >> /etc/apk/repositories \
  	\
  	# Add the packages that we need.
  	&& apk add --update --allow-untrusted \
  		"pycdp=${CDP_VERSION}-r0" \
  		"cdpt_all=${CDP_VERSION}-r0" \
  	# Move the old repositories back
  	&& mv /etc/apk/old-repositories /etc/apk/repositories \
  	# Clean up the dependencies downloaded by go.
  	&& apk del .build-deps \
  	&& rm -rf /var/cache/apk/* \
  	&& rm -rf /tmp/Packages*

ENV CDP_EXT_LIB_PATH /usr/lib/ext_lib
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
