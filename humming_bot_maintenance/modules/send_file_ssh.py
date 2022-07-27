
from datetime import datetime
import shutil
import subprocess
import os

def main(LOCAL_FOLDER):
    arg1 = input("Enter bot_instance\n")
    arg2 = input("Enter relative file path\n")
    input_args  = [arg1, arg2, ]
    subprocess.check_call([
            'wsl',f'{LOCAL_FOLDER}/shell_scripts/send_config.sh', *input_args
        ],
    )

if __name__ == '__main__':
    #load .env variables
    import os
    from dotenv import load_dotenv
    load_dotenv()
    PWD = os.getenv('PWD')
    import sys
    sys.path.insert(1, PWD)
    LOCAL_FOLDER = os.getenv('LOCAL_FOLDER')
    main(LOCAL_FOLDER)