{
set -e
set -x

export NUM_JOBS=1

source verif/sim/setup-env.sh
export DV_SIMULATORS=veri-testharness

DV_SIMULATORS=veri-testharness bash verif/regress/dv-riscv-arch-test.sh
DV_SIMULATORS=veri-testharness bash verif/regress/smoke-tests.sh
} > output.txt 2>&1