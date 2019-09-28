# coding: utf-8
import sys
sys.dont_write_bytecode = True
from common import Command

class Sample(Command):

    def command_name(self):
        return "Sample"
    
    def execute(self):
        pass


if __name__ == "__main__":
    sample = Sample()
    sample.main()