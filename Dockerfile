FROM predixadoption/edge-pycdp3:1.0.0

LABEL maintainer="Predix Builder Relations"
LABEL org="https://hub.docker.com/u/predixadoption"
LABEL version="1.0.33"
LABEL support="https://forum.predix.io"
LABEL license="https://github.com/PredixDev/predix-docker-samples/blob/master/LICENSE.md"

ENV LANG C.UTF-8

ENV CDP_CONFIG /opt/app_config/cdp_config.json

RUN pip3 install tornado

ENV CDP_EXT_LIB_PATH /usr/lib/ext_lib

ADD ./edgeworker/edgeworker.tar.gz /

COPY ./src/models /opt/microservice
COPY ./src/server /opt/webserver
COPY ./config /opt/cdp_config
COPY ./scripts/entry_point.sh /

WORKDIR /

RUN chmod +x entry_point.sh
ENV PYTHONPATH=$PYTHONPATH:/usr/local/lib/python3.5/site-packages

ENTRYPOINT ["/entry_point.sh"]
