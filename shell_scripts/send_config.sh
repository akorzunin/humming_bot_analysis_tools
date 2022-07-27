echo send_configs
. ./.env.sh

# for bot_name; do
echo $1
echo $2
# mkdir -p ./temp/${bot_name}/configs
# # send strategy config
scp ${LOCAL_FOLDER}/humming_bot_maintenance/${2} ${HUMMINGBOT_HOST_USER}@${HUMMINGBOT_HOST_IP}:${HUMMINGBOT_HOST_LOCATION}/${1}_files/hummingbot_conf/
    
# done