import os

file = "detected.txt"
logs = "/home/maveric/workspace/copies/logs/results_all"

with open(file, "r") as infile:
    content = infile.readlines()

ids = [line.split("/")[6] for line in content if "/maveric/" in line]


def parse_dir_1(directory):
    detected = []
    veri_erros = []
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            if dir not in ids:
                continue
            target_dir_path = logs + "/" + dir + "/" + "veri-testharness_sim"
            verilator_logs = [f for f in os.listdir(
                target_dir_path) if os.path.isfile(os.path.join(target_dir_path, f))]
            dot_logs = [log for log in verilator_logs if log.endswith(".log")]
            if dot_logs:
                detected.append(dir)
            else:
                veri_erros.append(dir)
    return detected, veri_erros


def parse_dir_2(directory):
    detected = []
    false_detected = []
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            flag = False
            if dir not in ids:
                continue
            target_dir_path = logs + "/" + dir + "/" + "veri-testharness_sim"
            verilator_logs = [f for f in os.listdir(
                target_dir_path) if os.path.isfile(os.path.join(target_dir_path, f))]
            for f in verilator_logs:
                f = target_dir_path + "/" + f
                with open(f, "r") as infile:
                    content = infile.read()
                if "failed" in content.lower():
                    flag = True
                    break
            if flag:
                detected.append(dir)
            else:
                false_detected.append(dir)
    return detected, false_detected


detected_1, veri_errors_1 = parse_dir_1(logs)
detected_1, veri_errors_1 = set(detected_1), set(veri_errors_1)

detected_2, veri_errors_2 = parse_dir_2(logs)
detected_2, veri_errors_2 = set(detected_2), set(veri_errors_2)

detected = detected_1.union(detected_2)
veri_errors = veri_errors_1.intersection(veri_errors_2)


print("Truly detected:", len(detected))
print("Verilator error:", len(veri_errors))
