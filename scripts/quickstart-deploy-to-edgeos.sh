#!/bin/bash

set -e

trap "trap_ctrlc" 2

ROOT_DIR=$(pwd)
SKIP_BROWSER="0"
function local_read_args() {
  while (( "$#" )); do
  opt="$1"
  case $opt in
    -h|-\?|--\?--help)
      PRINT_USAGE=1
      QUICKSTART_ARGS="$SCRIPT $1"
      break
    ;;
    -b|--branch)
      BRANCH="$2"
      QUICKSTART_ARGS+=" $1 $2"
      shift
    ;;
    -o|--override)
      RECREATE_TAR="1"
      QUICKSTART_ARGS=" $SCRIPT"
    ;;
    --skip-setup)
      SKIP_SETUP=true
    ;;
    *)
      QUICKSTART_ARGS+=" $1"
      #echo $1
    ;;
  esac
  shift
  done

  if [[ -z $BRANCH ]]; then
    echo "Usage: $0 -b/--branch <branch> [--skip-setup]"
    exit 1
  fi
}

if [[ $(docker pull dtr.predix.io/predix-edge/predix-edge-mosquitto-amd64:latest) ]]; then
  echo "pull successfully"
else
  read -p "Enter your DTR user name> " DTR_USERNAME
  read -p "Enter your DTR password> " -s DTR_PASSWORD
  docker login dtr.predix.io -u $DTR_USERNAME -p $DTR_PASSWORD
  docker pull dtr.predix.io/predix-edge/predix-edge-mosquitto-amd64:latest
fi

#docker pull predixadoption/edge-hello-world:latest
pwd
HELLO_WORLD_APP="hello-world-app.tar.gz"

if [[ "$RECREATE_TAR" == "1" || ! -e "images.tar" ]]; then
  echo "Creating a images.tar with required images"
  rm -rf images.tar
  docker save -o images.tar predixadoption/edge-hello-world:latest
fi
if [[ "$RECREATE_TAR" == "1" || ! -e "$HELLO_WORLD_APP" ]]; then
  rm -rf $HELLO_WORLD_APP
  echo "Creating $HELLO_WORLD_APP with docker-compose.yml"
  tar -czvf $HELLO_WORLD_APP images.tar docker-compose.yml
fi

HELLO_WORLD_CONFIG="hello-world-config.zip"

if [[ "$RECREATE_TAR" == "1" || ! -e "$HELLO_WORLD_CONFIG" ]]; then
  rm -rf $HELLO_WORLD_CONFIG
  echo "Compressing the configurations."
  cd config
  zip -X -r ../$HELLO_WORLD_CONFIG *.json
  cd ../
fi

read -p "Enter the IP Address of Edge OS> " IP_ADDRESS
read -p "Enter the username for Edge OS> " LOGIN_USER
read -p "Enter your user password> " -s LOGIN_PASSWORD

pwd
expect -c "
  spawn scp -o \"StrictHostKeyChecking=no\" $HELLO_WORLD_APP $HELLO_WORLD_CONFIG scripts/quickstart-run-wind-workbench.sh docker-compose_services.yml $LOGIN_USER@$IP_ADDRESS:/mnt/data/downloads
  set timeout 50
  expect {
    \"Are you sure you want to continue connecting\" {
      send \"yes\r\"
      expect \"assword:\"
      send "$LOGIN_PASSWORD\r"
    }
    \"assword:\" {
      send \"$LOGIN_PASSWORD\r\"
    }
  }
  expect \"*\# \"
  spawn ssh -o \"StrictHostKeyChecking=no\" $LOGIN_USER@$IP_ADDRESS
  set timeout 5
  expect {
    \"Are you sure you want to continue connecting\" {
      send \"yes\r\"
      expect \"assword:\"
      send \"$LOGIN_PASSWORD\r\"
    }
    "assword:" {
      send \"$LOGIN_PASSWORD\r\"
    }
  }
  expect \"*\# \"
  send \"su eauser /mnt/data/downloads/quickstart-run-wind-workbench.sh\r\"
  set timeout 20
  expect \"*\# \"
  send \"exit\r\"
  expect eof
"

sleep 10
# Automagically open the application in browser, based on OS
if [[ $SKIP_BROWSER == 0 ]]; then
  app_url="http://$IP_ADDRESS:9098"

  case "$(uname -s)" in
     Darwin)
       # OSX
       open $app_url
       ;;
     Linux)
       # OSX
       xdg-open $app_url
       ;;
     CYGWIN*|MINGW32*|MINGW64*|MSYS*)
       # Windows
       start "" $app_url
       ;;
  esac
fi
########### custom logic ends here ###########

#scp app.tar.gz config.zip scripts/quickstart-run-wind-workbench.sh root@$IP_ADDRESS:/mnt/data/downloads
