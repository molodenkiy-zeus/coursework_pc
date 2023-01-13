from cmd_interface import CmdInterface
from inv_index import InvertedIndex

if __name__ == '__main__':
    thread_no = 5
    index = InvertedIndex(thread_no)

    interface = CmdInterface(index)
    interface.run()