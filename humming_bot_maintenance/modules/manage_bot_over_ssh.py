
from datetime import datetime
import shutil
import subprocess
import os
# copy trade log from all bot instances

def copy_files_from_bot(bot_instances: list, file_type: str, LOCAL_FOLDER: str) -> int:
    # sourcery skip: collection-into-set, merge-duplicate-blocks
    '''file_type: [ logs, configs, *]'''
    # load_env_sh(LOCAL_FOLDER)
    if file_type in ['logs', ]:
        return subprocess.check_call([
            'wsl',f'{LOCAL_FOLDER}/shell_scripts/copy_configs.sh', *bot_instances
        ])
    elif file_type in ['configs', 'conf']:
        return subprocess.check_call([
            'wsl',f'{LOCAL_FOLDER}/shell_scripts/copy_configs.sh', *bot_instances
        ])
    else: 
        return subprocess.check_call([
                'wsl',f'{LOCAL_FOLDER}/shell_scripts/copy_configs.sh', *bot_instances
            ]), subprocess.check_call([
                'wsl',f'{LOCAL_FOLDER}/shell_scripts/copy_logs.sh', *bot_instances
            ]) 

def send_files_to_bot(bot_instances: list, LOCAL_FOLDER: str, file_type: str = None) -> int:
    if file_type: # TODO add different file types support
        return subprocess.check_call([
                'wsl',f'{LOCAL_FOLDER}/shell_scripts/send_configs.sh', *bot_instances
            ],
        )
            
def archive_files(research_name: str, add_date: bool = False):
    if add_date:
        research_name += f'_{str(datetime.now().date())}'
    # mkdir in archive
    os.makedirs(f'./archive/{research_name}/', exist_ok=True)
    # copy file from temp/hummng_bot*
    source = './temp/'
    destination = f'./archive/{research_name}/'
    shutil.copytree(source, destination, dirs_exist_ok=True)

if __name__ == '__main__':
    #load .env variables
    import os
    from dotenv import load_dotenv
    import sys
    load_dotenv()
    PWD = os.getenv('PWD')
    sys.path.insert(1, PWD)

    LOCAL_FOLDER = os.getenv('LOCAL_FOLDER')
    try:
        instances = sys.argv[2]
    except IndexError:
        from humming_bot_maintenance.bot_instances import instances
    if (arg := sys.argv[1]) == '--copy':
        copy_files_from_bot(
            bot_instances=instances,
            file_type='all',
            LOCAL_FOLDER=LOCAL_FOLDER,
        )
    elif arg == '--send':
        send_files_to_bot(
            bot_instances=instances, 
            file_type=1,
            LOCAL_FOLDER=LOCAL_FOLDER,
        )
    else:
        print('wrong argument: ', arg)