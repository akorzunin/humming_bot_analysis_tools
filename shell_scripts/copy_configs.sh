echo cpconfigs
. ./.env.sh

for bot_name; do
    echo $bot_name
    mkdir -p ./temp/${bot_name}/configs
    # dl file from note_ssh
    scp ${HUMMINGBOT_HOST_USER}@${HUMMINGBOT_HOST_IP}:${HUMMINGBOT_HOST_LOCATION}/${bot_name}_files/hummingbot_conf/conf* ${LOCAL_FOLDER}/temp/${bot_name}/configs/
    # TODO copy global config

done