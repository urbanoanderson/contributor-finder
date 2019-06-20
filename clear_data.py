import os
import shutil
    
if __name__ == '__main__':
    print('Clearing old data...')
    shutil.rmtree('repos/')
    os.mkdir('repos/')