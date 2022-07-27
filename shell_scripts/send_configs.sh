echo send_configs
. ./.env.sh

for bot_name; do
    echo $bot_name
    mkdir -p ./temp/${bot_name}/configs
    # send strategy config
    scp ${LOCAL_FOLDER}/humming_bot_maintenance/generated_configs/${bot_name}/conf* ${HUMMINGBOT_HOST_USER}@${HUMMINGBOT_HOST_IP}:${HUMMINGBOT_HOST_LOCATION}/${bot_name}_files/hummingbot_conf/
    
donea