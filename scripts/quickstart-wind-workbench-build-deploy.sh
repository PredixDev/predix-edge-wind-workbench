#!/bin/bash
set -e

trap "trap_ctrlc" 2

ROOT_DIR=$(pwd)
logDir="$ROOT_DIR/predix-scripts/log"
EDGE_STARTER_NETWORK="edgeservices_cdp_network"
EDGE_STARTER_IMAGE_MQTT="dtr.predix.io/predix-edge/predix-edge-mosquitto-amd64"
EDGE_STARTER_IMAGE_REDIS="registry.gear.ge.com/predix_edge/redis-amd64"
EDGE_STARTER_IMAGE_WIND_WORK_BENCH="registry.gear.ge.com/predix_edge/wind-workbench:0.1"

EDGE_STARTER_INSTANCE_NAME_REDIS="edgeservices_cdp_redis"
EDGE_STARTER_INSTANCE_NAME_MQTT="edgeservices_cdp_mqtt"
EDGE_STARTER_INSTANCE_NAME_WIND_WORKBENCH="windturbine"
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



BRANCH="master"
PRINT_USAGE=0
SKIP_SETUP=false
#ASSET_MODEL="-amrmd predix-ui-seed/server/sample-data/predix-asset/asset-model-metadata.json predix-ui-seed/server/sample-data/predix-asset/asset-model.json"
SCRIPT="-script build-basic-app.sh -script-readargs edge-starter-readargs.sh"
QUICKSTART_ARGS=" $SCRIPT"
VERSION_JSON="version.json"
PREDIX_SCRIPTS=predix-scripts
REPO_NAME=wind-workbench
VERSION_JSON="version.json"
APP_DIR="edge-hello-world"
APP_NAME="Edge Starter Hello World"
TOOLS="Docker, Git"
TOOLS_SWITCHES="--docker --git"

local_read_args $@
IZON_SH="https://raw.githubusercontent.com/PredixDev/izon/$BRANCH/izon.sh"
VERSION_JSON_URL=https://raw.githubusercontent.com/PredixDev/$REPO_NAME/$BRANCH/version.json


function check_internet() {
  set +e
  echo ""
  echo "Checking internet connection..."
  curl "http://google.com" > /dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "Unable to connect to internet, make sure you are connected to a network and check your proxy settings if behind a corporate proxy"
    echo "If you are behind a corporate proxy, set the 'http_proxy' and 'https_proxy' environment variables."
    exit 1
  fi
  echo "OK"
  echo ""
  set -e
}

function init() {
  currentDir=$(pwd)
  if [[ $currentDir == *"scripts" ]]; then
    echo 'Please launch the script from the root dir of the project'
    exit 1
  fi
  if [[ ! $currentDir == *"$REPO_NAME" ]]; then
    mkdir -p $APP_DIR
    cd $APP_DIR
  fi

  check_internet

  #get the script that reads version.json
  eval "$(curl -s -L $IZON_SH)"

  getVersionFile
  getLocalSetupFuncs
}

if [[ $PRINT_USAGE == 1 ]]; then
  init
  __print_out_standard_usage
else
  if $SKIP_SETUP; then
    init
  else
    init
    __standard_mac_initialization
  fi
fi

getPredixScripts
#clone the repo itself if running from oneclick script
getCurrentRepo

echo "quickstart_args=$QUICKSTART_ARGS"
source $PREDIX_SCRIPTS/bash/quickstart.sh $QUICKSTART_ARGS

########### custom logic starts here ###########
if ! [ -d "$logDir" ]; then
  mkdir "$logDir"
  chmod 744 "$logDir"
fi
touch "$logDir/quickstart.log"

cd $REPO_NAME

docker-compose -f docker-compose_build.yml build
docker-compose -f docker-compose_build.yml up -d

# Automagically open the application in browser, based on OS
if [[ $SKIP_BROWSER == 0 ]]; then
  app_url="http://localhost:9098"

  case "$(uname -s)" in
     Darwin)
       # OSX
       open $app_url
       ;;

     CYGWIN*|MINGW32*|MINGW64*|MSYS*)
       # Windows
       start "" $app_url
       ;;
  esac
fi
__append_new_line_log "Successfully completed $APP_NAME installation!" "$logDir"
__append_new_line_log "" "$logDir"
