hex_matrix = []

for x in range(15):
    hex_list = []
    hex_matrix.append(hex_list)

    for y in range(16):
        int = (x*16) + y + 1
        hex_list.append(int)

print(hex_matrix)

print(hex_matrix.index([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]))

print(hex_matrix.index())