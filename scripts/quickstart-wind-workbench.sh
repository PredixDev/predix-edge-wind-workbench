#!/bin/bash
set -e

trap "trap_ctrlc" 2

ROOT_DIR=$(pwd)
logDir="$ROOT_DIR/predix-scripts/log"

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

IZON_SH="https://raw.githubusercontent.com/PredixDev/izon/master/izon2.sh"
#ASSET_MODEL="-amrmd predix-ui-seed/server/sample-data/predix-asset/asset-model-metadata.json predix-ui-seed/server/sample-data/predix-asset/asset-model.json"
REPO_NAME="wind-workbench"
DOCKER_STACK_NAME="edge-hello-world"
SCRIPT="-script edge-starter-deploy.sh -script-readargs edge-starter-deploy-readargs.sh --run-edge-app"
QUICKSTART_ARGS=" $SCRIPT -repo-name $REPO_NAME -app-name $DOCKER_STACK_NAME"
VERSION_JSON="version.json"
PREDIX_SCRIPTS="predix-scripts"
VERSION_JSON="version.json"
APP_DIR="edge-hello-world"
APP_NAME="Edge Starter Hello World"
GITHUB_RAW="https://raw.githubusercontent.com/PredixDev"

TOOLS="Docker, Git"
TOOLS_SWITCHES="--docker --git"

# Process switches
local_read_args $@

VERSION_JSON_URL="$GITHUB_RAW/$REPO_NAME/$BRANCH/version.json"


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
pwd
ls -lrt
#if [[ ! -d "$PREDIX_SCRIPTS/$REPO_NAME" ]]; then
#  echo "repo not present"
getCurrentRepo
#fi
echo "pwd after copy -> $(pwd)"
ls -lrt
echo "quickstart_args=$QUICKSTART_ARGS"
docker pull predixadoption/edge-hello-world:latest

source $PREDIX_SCRIPTS/bash/quickstart.sh $QUICKSTART_ARGS

########### custom logic starts here ###########
if ! [ -d "$logDir" ]; then
  mkdir "$logDir"
  chmod 744 "$logDir"
fi

docker service ls

sleep 30

# Automagically open the application in browser, based on OS
if [[ $SKIP_BROWSER == 0 ]]; then
  app_url="http://127.0.0.1:9098"

  case "$(uname -s)" in
     Darwin)
       # OSX
       open $app_url
       ;;
     Linux)
       # LINUX
       if [[ $( which xdg-open | wc -l ) == 1 ]]; then
          xdg-open $app_url
       fi
       ;;
     CYGWIN*|MINGW32*|MINGW64*|MSYS*)
       # Windows
       start "" $app_url
       ;;
  esac
fi
########### custom logic ends here ###########
docker service ls
echo ""
echo ""
docker network ls

echo "" >> $SUMMARY_TEXTFILE
echo "Edge Hello world URL: http://127.0.0.1:9098" >> $SUMMARY_TEXTFILE
echo "" >> $SUMMARY_TEXTFILE

cat $SUMMARY_TEXTFILE
echo "......................................Done......................................"
