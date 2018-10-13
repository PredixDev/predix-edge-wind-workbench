# Wind Workbench
A Workbench that presents a simulated wind environment that will allow folks to learn elements of the Edge


![Happy Day](/assets/BadScreenCaptureOfEdgeWindWorkbench.png?raw=true "Workbench")

## Installation


### Dependencies

- Docker - See install docs at  https://edge.portal.ge.com/guides/dev-env/docker/

### 1) Clone the repo in desired location

```bash
$ git clone https://github.com/PredixDev/wind-workbench.git
```

### 2) Move into directory

```bash
$ cd wind-workbench
```

### 3) Create docker image and run container

```bash
$ docker-compose up -d
```

### 4) Check to see if container and image are running

```bash
$ docker ps
$ docker images
```

*Windturbine should be listed in both*

### 5) Check logs

```bash
$ docker logs windturbine
```

*Logs should be generated on the command line*

### 6) If running in Virtual Box, configure Port Forwarding to host machine

From the VirtualBox VM window menu, select:

Devices > Network > Network Settings...

- Click on Port Forwarding
- Click Insert New Rule button
- Set Host Port to `9098`
- Set Guest Port to `9098`

### 7) Open edgeWindWorkbench UI

Open Chrome browser on your host machine to http://127.0.0.1:9098/

*May have problems if opening in other browsers*

### To shutdown edgeWindWorkbench container:

In wind-workbench directory...
```bash
$ docker-compose down
```

### To build locally:

The docker-compose.yml file pulls image the wind workbench image from dtr to save build time,
if you want to make changes and build it locally run...
```bash
$ docker-compose -f docker-compose_build.yml build
```
and then
```bash
$ docker-compose -f docker-compose_build.yml up -d
```

[![Analytics](https://ga-beacon.appspot.com/UA-82773213-1/wind-workbench/readme?pixel)](https://github.com/PredixDev)
