import os
from dotenv import load_dotenv
load_dotenv()
PWD = os.getenv('PWD')
import sys
sys.path.insert(1, os.path.join(PWD, 'modules', 'alg_modules'))
