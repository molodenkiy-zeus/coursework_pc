import matplotlib.pyplot as plt

from inv_index import InvertedIndex


if __name__ == '__main__':
    th_no = [1, 10, 20, 30, 40, 50]
    path = 'E:/datasets/aclImdb'
    iter_no = 1

    variant = 53

    perf = []
    for th in th_no:
        time = 0
        index = InvertedIndex(th, V=variant)
        for i in range(iter_no):
            print(f'{th}_{i}')
            index.clear()
            time += index.process(path, benchmark=True)
        perf.append(time / iter_no)

    plt.plot(th_no, perf)
    plt.xlabel('thread number')
    plt.ylabel('time, s')
    plt.show()
