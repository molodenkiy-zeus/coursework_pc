import math
import os
import string
import time
from collections import defaultdict
from multiprocessing import Manager
from multiprocessing.pool import Pool
from typing import Optional

import numpy as np


class InvertedIndex:
    def __init__(self, thread_no: int = 1, batch_size: int = 50, V: Optional[int] = None):
        self.V = V
        self.batch_size = batch_size

        self._manager = Manager()
        self._split = self._manager.list()
        self._lock = self._manager.Lock()
        if thread_no <= 0:
            raise Exception('Number of processes must be at least 1')
        self._th_no = thread_no
        self._map = defaultdict(list)

    def __getstate__(self):
        self_dict = self.__dict__.copy()
        del self_dict['_manager']
        return self_dict

    def process(self, path: str, benchmark: bool = False):
        if self.V is None:
            files = self._traverse_dir(path)
        else:
            files = self._traverse_dir_alt(path, self.V)

        if self._th_no == 1:
            ret = [self._single_thread(files)]
        else:
            if len(files) > self.batch_size * self._th_no:
                split = np.array_split(files, math.ceil(len(files)/self.batch_size))
                init_split = split[:self._th_no]
                self._split = split[self._th_no:]
            else:
                init_split = np.array_split(files, self._th_no)

            _pool = Pool(processes=self._th_no)
            ret = _pool.map(self._single_thread, init_split)
            _pool.close()
            _pool.join()
        return self._process_data(ret, benchmark)

    def search(self, word: str):
        return self._map[word.translate(str.maketrans('', '', string.punctuation)).lower()]

    def clear(self):
        self._map = defaultdict(list)

    def _single_thread(self, files):
        start = time.perf_counter()
        aux = []

        while True:
            for file in files:
                with open(file, 'r', encoding="utf8") as fp:
                    data = fp.read().replace('<br />', ' ').replace('<br /><br />', ' ').translate(
                        str.maketrans('', '', string.punctuation))
                split = data.split()
                for i in range(len(split)):
                    word = split[i].lower()
                    aux.append((word, file, i))

            if len(self._split) != 0:
                with self._lock:
                    files = self._split.pop(-1)
            else:
                break
        return aux, time.perf_counter() - start

    def _traverse_dir(self, path):
        f = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            f.extend([os.path.join(dirpath, path).replace('\\', '/') for path in filenames])
        return f

    def _traverse_dir_alt(self, path, V):
        f = []
        ret = []
        for (dirpath, dirnames, filenames) in os.walk(path):
            f.extend([os.path.join(dirpath, dir).replace('\\', '/') for dir in dirnames])

        for d in f:
            files = os.listdir(d)
            N = len(files)
            if N > 10:
                files = {int(f_name.replace('.txt', '').split('_')[0]): os.path.join(d, f_name) for f_name in files}
                start = int((N / 50 * (V - 1)) % N)
                end = int((N / 50 * V) % N)
                for f_id, f_name in files.items():
                    if start <= f_id < end:
                        ret.append(f_name)
        return ret

    def _process_data(self, ret, benchmark=False):
        s = []
        _s = time.perf_counter()
        for aux in ret:
            for record in aux[0]:
                self._map[record[0]].append((record[1], record[2]))
            if benchmark:
                s.append(aux[1])
        return sum(s) / len(s) + time.perf_counter() - _s if benchmark and len(s) != 0 else None
