{
# export CI_CORES=4

# ===== check =====
bash ci/check_design.sh $CI_CORES
bash ci/lint.sh verilator $CI_CORES
bash ci/yosys.sh $CI_CORES


# ===== test-short =====
# vcs only
bash ci/bloodgraph.sh $CI_CORES
bash ci/dcache_regress.sh verilator $CI_CORES
bash ci/icache_regress.sh verilator $CI_CORES

bash ci/me_regress.sh verilator $CI_CORES
bash ci/single_core_atomics.sh verilator $CI_CORES
bash ci/single_core_testlist.sh verilator RISCV_TESTLIST $CI_CORES
bash ci/weird_config.sh verilator $CI_CORES


# ===== test-medium =====
bash ci/check_loops.sh $CI_CORES
bash ci/l2e_config.sh verilator $CI_CORES
bash ci/surelog.sh $CI_CORES

# vcs only
bash ci/accelerator.sh verilator $CI_CORES

bash ci/checkpoint.sh verilator $CI_CORES
bash ci/single_core_testlist.sh verilator MISC_TESTLIST $CI_CORES


# ===== test-long =====
bash ci/single_core_testlist.sh verilator BEEBS_TESTLIST $CI_CORES
bash ci/single_core_testlist.sh verilator COREMARK_TESTLIST $CI_CORES

} > output.txt 2>&1
