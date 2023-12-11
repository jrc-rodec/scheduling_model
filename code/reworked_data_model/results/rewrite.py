file_path = r"C:\Users\dhutt\Downloads\part_1.txt"
benchmark_base_path = r"C:\Users\dhutt\Desktop\SCHEDULING_MODEL\code\external_test_data\FJSSPinstances\\"
file = open(file_path, 'r')
file_content = file.readlines()
new_file_content = []
for line in file_content[:402]:
    data = line.split(';')
    new_file_content.append(f'{data[0]};{data[1]};{data[2]};{data[5]};{data[6]};{data[7]};{data[8]};{data[9]}\n')

new_file_content.insert(0, 'Source;Instance;BestObjective;Gap;Status;NExploredSolutions;OptimizationTime;OverallTime\n')
target_file = r"C:\Users\dhutt\Desktop\SCHEDULING_MODEL\code\reworked_data_model\results\30min_gurobi.txt"

file = open(target_file, 'w')
for line in new_file_content:
    # TODO: remove x, y, c vectors
    file.write(line)
file.close()