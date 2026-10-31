"""Runtime hook so llama-cpp finds its libs inside the PyInstaller bundle.
Temp folder is forced next to the EXE."""
import os
import sys

if getattr(sys, 'frozen', False):
    # Running as EXE — temp lives next to the EXE
    base = sys._MEIPASS
    llama_lib = os.path.join(base, 'llama_cpp', 'lib')
    if os.path.isdir(llama_lib):
        os.environ['PATH'] = llama_lib + os.pathsep + os.environ.get('PATH', '')
        os.environ['LLAMA_CPP_LIB'] = llama_lib
