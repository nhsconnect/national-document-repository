with open("input_dataset.csv.all", "r") as f:
    lines = f.readlines()

for i in range(len(lines)):
    if i % 2 == 0:
        lines[i] = lines[i].rstrip("\n") + f" {500}\n"

with open("input_dataset.csv.all", "w") as f:
    f.writelines(lines)
