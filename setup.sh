#!/bin/bash

# Run setup scripts for different components of qaas script.
run_component_setup() {
  # Currently under the directory of setup.sh
  for component in qaas-extractor qaas-web qaas-backplane; do
  # for component in qaas-web; do
    cd ${component}
    ./setup.sh
    cd ..
  done

}

if [[ ${USER} != "qaas" ]]; then
  echo "OUTSIDE container setting up local image"
  # Build local image


  echo -n "Enter Qaas user password:"
  read -s QAAS_PASSWORD
  echo
  export QAAS_PASSWORD

  # Collect DB password early to make the setup.sh process runs more smoothly
  echo -n "Enter Qaas DB user password:"
  read -s QAAS_DB_PASSWORD
  echo
  export QAAS_DB_PASSWORD

  SSH_PARENT_FOLDER=$(readlink -f ~/)
  echo -n "Enter the folder parent of .ssh folder which has SSH configuration and key for webdb and backplane container (Press enter for $SSH_PARENT_FOLDER):"
  read ssh_parent_folder_input
  if [ ! -z $ssh_parent_folder_input ]; then
    SSH_PARENT_FOLDER=${ssh_parent_folder_input}
  fi
  export SSH_PARENT_FOLDER

  while true; do
    echo "Oneview FLOPS collection requires executing sudo sysctl command."
    echo -n "Do you want to enable? (Y/N): "
    read answer
    case $answer in
      [Yy])
        if sudo sysctl kernel.perf_event_paranoid=-1; then
          echo "Oneview FLOPS collection enabled successfully."
          break
        else
          echo "sudo command falied."
        fi
        ;;
      [Nn])
        echo "Proceeding with Oneview FLOPS collection disabled."
        break
        ;;
      *)
        echo "Invalid choice. Please enter 'Y' or 'N'."
        ;;
    esac
  done

  echo -n "Customized dockerfile for backplane container (Press enter for none):"
  read custom_dockerfile

  echo -n "Enter port for web service: "
  read web_port
  echo "declare -A port_map=( [2222:22]=qaas_backplane [${web_port}:80]=qaas_webdb [443:443]=qaas_webdb [3000:3000]=qaas_webdb )" > ./container/port_map.sh

  # First stop running containers
  ./container/stop-container.sh
  pushd container
  if [ -z $custom_dockerfile ]; then
    . ./build-local-image.sh
  else
    echo "Customized dockerfile: ${custom_dockerfile}"
    . ./build-local-image.sh -f $custom_dockerfile
  fi
  popd
  # QAAS_PASSWORD set here but Still sourced the above script in case it decided to change password of qaas

  # Setup components outside the container
  run_component_setup

  env_secret_file=$(mktemp)
  echo "QAAS_PASSWORD=${QAAS_PASSWORD}" > ${env_secret_file}
  echo "QAAS_DB_PASSWORD=${QAAS_DB_PASSWORD}" >> ${env_secret_file}
  # Run this script again inside to set up the rest
  echo "Proceed rest of setup INSIDE WEBDB container"
  ./container/run-container.sh -e ${env_secret_file} -i local_image_qaas_webdb:latest ./setup.sh
  echo "Proceed rest of setup INSIDE BACKPLANE container"
  ./container/run-container.sh -e ${env_secret_file} -i local_image_qaas_backplane:latest ./setup.sh
  rm ${env_secret_file}

  #don't put setup.sh next to run container, it thinks it is a parameter, instead just call setup in run container
  #./container/run-container.sh 
  # Done, quit and not the execute code below.
else
  echo "INSIDE ${QAAS_CONTAINER_NAME} container setting up TOPMOST script"
  run_component_setup
  #start server
  # SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
  # start_server_script_path=$SCRIPT_DIR/qaas-web/deployment/start_server.py
  # python3 ${start_server_script_path}

  # exec su qaas
fi
