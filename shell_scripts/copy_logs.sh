echo cplogs
. ./.env.sh

for bot_name; do
    echo $bot_name
    mkdir -p ./temp/${bot_name}/logs
    # dl file from note_ssh
    scp ${HUMMINGBOT_HOST_USER}@${HUMMINGBOT_HOST_IP}:${HUMMINGBOT_HOST_LOCATION}/${bot_name}_files/hummingbot_logs/* ${LOCAL_FOLDER}/temp/${bot_name}/logs/

done