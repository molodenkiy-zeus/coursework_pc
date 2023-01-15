import os.path
from collections import defaultdict

from inv_index import InvertedIndex


class CmdInterface:
    def __init__(self, index: InvertedIndex):
        self.index = index
        self.path = ''

    def run(self):
        print('index running')
        while True:
            cmd = input('>').split()
            if cmd[0] == 'add_path':
                self.__add(cmd)
            elif cmd[0] == 'config_path':
                self.path = cmd[1]
            elif cmd[0] == 'add':
                self.__add_v_config(cmd)
            elif cmd[0] == 'clear':
                self.index.clear()
                print(f'index empty')
            elif cmd[0] == 'search':
                self.__search(cmd)
            elif cmd[0] == 'stop':
                self.index.clear()
                break
            elif cmd[0] == 'help':
                print('index add {path}\n'
                      'index clear\n'
                      'index search {word1} {word2}\n'
                      'index stop')
            else:
                print('Unknown command')

    def __add(self, cmd):
        path = cmd[1]
        if os.path.exists(path):
            self.index.process(path)
            print(f'New files added')
        else:
            print(f'{path} does not exists')

    def __add_v_config(self, cmd):
        path = os.path.join(self.path, cmd[1])
        if os.path.exists(path):
            self.index.process(path)
            print(f'New files added')
        else:
            print(f'{path} does not exists')

    def __search(self, cmd):
        keywords = cmd[1:]
        res_count = defaultdict(int)
        res = defaultdict(list)
        for word in keywords:
            for ret in self.index.search(word):
                res_count[ret[0]] += 1
                res[ret[0]].append(ret[1])
        for file, count in res_count.items():
            if count == len(keywords):
                print(f'{file} {res[file]}')
