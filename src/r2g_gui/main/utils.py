def compare_version(v1, v2):
    v1 = v1.strip().split('.')
    v2 = v2.strip().split('.')
    v1 += (max(len(v1), len(v2)) - len(v1)) * ['0']
    v2 += (max(len(v1), len(v2)) - len(v2)) * ['0']
    for i in range(len(v1)):
        if int(v1[i]) > int(v2[i]):
            return "1"  # version 1 is newer
        elif int(v1[i]) < int(v2[i]):
            return "2"  # version 2 is newer
        else:
            continue
    return "0"  # equal
