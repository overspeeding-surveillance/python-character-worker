# sorting based on xmin
def sort(list):
    for i in range(0, len(list) - 1):
        for j in range(0, len(list) - 1):
            if (list[j][0] > list[j+1][0]):
                temp = list[j+1]
                list[j+1] = list[j]
                list[j] = temp

    return list
