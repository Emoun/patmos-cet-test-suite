import os
import subprocess
import sys
from shutil import which
import re
import random

if which("patmos-clang") is None:
    print("Patmos simulator 'patmos-clang' could not be found.")
    sys.exit(1)

if which("pasim") is None:
    print("Patmos simulator 'pasim' could not be found.")
    sys.exit(1)
    
# Parse arguments
   
# The source file to test
source_to_test = sys.argv[1]

# The compiled file
compiled = sys.argv[2]   

# Which function is the root single-path function
sp_root = sys.argv[3]

check_all = len(sys.argv) > 4 and sys.argv[4]=="true"

# Compile and test using the given compiler arguments.
# if 'ensure_all' is true, checks that running the program with any seed executes successfully.
# if false, only checks when given the seed 0
def compile_and_test(args, ensure_all):
    def throw_error(*msgs):
        for msg in msgs:
            print(msg, end = '')
        print("\nCompiler args: ", args)
        sys.exit(1)
             
    def run_and_time(seed, must_exec_correct):
        out = subprocess.run(["pasim", compiled, "--print-stats", sp_root],stderr=subprocess.PIPE,input=str(seed), encoding='ascii')
        if must_exec_correct and out.returncode != 0:
            throw_error("Execution failed for '", compiled, "' using seed ", 0)
        
        cycles = re.findall('Cycles:\s*[0-9]+',out.stderr)
        
        if len(cycles) == 1: 
            return int(cycles[0].split(":")[1].strip())
        else:
            throw_error("Couldn't unambiguously find the cycles count using seed '", seed, "': ", out.stderr)
             
    compiler_args = source_to_test + " -o " + compiled + " -mllvm --mpatmos-singlepath=" + sp_root + " -mllvm --mpatmos-enable-cet " + args
    #compiler_args = source_to_test + " -o " + compiled + " " + args
             
    # Compile
    if subprocess.run(["patmos-clang"] + compiler_args.split()).returncode != 0:
        throw_error("Failed to compile '", source_to_test, "'")
    
    # Run with seed 0
    cycles = run_and_time(0, True)
    
    for i in range(0,10):
        seed = random.randint(0, 2147483647) #32-bit int
        next_cycles = run_and_time(seed, ensure_all)
        
        if next_cycles != cycles:
            throw_error("Unequal execution time seed '", seed, "'") 

compile_and_test("-O2", False)

# Success
sys.exit(0)