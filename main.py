import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lexico'))

if __name__ == "__main__":
    from interfaces.mainInterface import MainInterface
    MainInterface().mainloop()
