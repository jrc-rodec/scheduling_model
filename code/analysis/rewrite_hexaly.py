with open(r'C:\Users\huda\Downloads\results_hexaly.txt', 'r') as in_file:
    lines = in_file.readlines()
    result = []
    for line in lines:#[-1:]:
        data = line.split(';')
        if data[2] == data[3]:
            data[1] = '1'

        result.append(';'.join(data))
        #print(result)
    with open(r'C:\Users\huda\Downloads\results_hexaly_rewritten.txt', 'w') as out_file:
        out_file.writelines(result)
