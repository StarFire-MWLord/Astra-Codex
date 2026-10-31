"""Runtime hook so llama-cpp finds its libs inside the PyInstaller bundle."""
import os
import sys

if getattr(sys, 'frozen', False):
    # Running as EXE
    base = sys._MEIPASS
    llama_lib = os.path.join(base, 'llama_cpp', 'lib')
    if os.path.isdir(llama_lib):
        # Prepend so Windows loads our DLLs first
        os.environ['PATH'] = llama_lib + os.pathsep + os.environ.get('PATH', '')
        # Also set for some llama-cpp builds that look here
        os.environ['LLAMA_CPP_LIB'] = llama_lib
