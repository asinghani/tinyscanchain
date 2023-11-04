# tinyscanchain

Playing with generating tiny scan chains for TinyTapeout-style projects.

The current limitation is that the insertion is done pre-optimization, so this may prevent deduplication of DFFs.

Usage: tinyscanchain.py [infile.sv] [top_module] [outfile.sv] [logfile.txt]
