{
# export CI_CORES=4

# ===== check =====
bash ci/check_design.sh 
bash ci/lint.sh verilator 
bash ci/yosys.sh 


# ===== test-short =====
# vcs only
bash ci/bloodgraph.sh 
bash ci/dcache_regress.sh verilator 
bash ci/icache_regress.sh verilator

bash ci/me_regress.sh verilator 
bash ci/single_core_atomics.sh verilator 
bash ci/single_core_testlist.sh verilator RISCV_TESTLIST 
bash ci/weird_config.sh verilator 


# ===== test-medium =====
bash ci/check_loops.sh 
bash ci/l2e_config.sh verilator 
bash ci/surelog.sh 

# vcs only
bash ci/accelerator.sh verilator 

bash ci/checkpoint.sh verilator 
bash ci/single_core_testlist.sh verilator MISC_TESTLIST 


# ===== test-long =====
bash ci/single_core_testlist.sh verilator BEEBS_TESTLIST 
bash ci/single_core_testlist.sh verilator COREMARK_TESTLIST 

} > output.txt 2>&1
