#https://github.com/lancaster-university/microbit-dal/blob/master/source/core/MicroBitDevice.cpp

def get_microbit_name(serial_number):
    n = int(serial_number)
    name_len = 5
    code_letters = 5
    codebook = [
        ['z', 'v', 'g', 'p', 't'],
        ['u', 'o', 'i', 'e', 'a'],
        ['z', 'v', 'g', 'p', 't'],
        ['u', 'o', 'i', 'e', 'a'],
        ['z', 'v', 'g', 'p', 't']
    ]

    ld = 1
    d = code_letters
    name = ""

    for i in range(name_len):
        h = int((n % d) / ld);
        n -= h;
        d *= code_letters;
        ld *= code_letters;
        name = codebook[i][h] + name

    return name

print(get_microbit_name(384933164)) #puvit
print(get_microbit_name(1252840479.9999999)) #tetoz
print(get_microbit_name(671265031)) #tuvov
print(get_microbit_name(20458004765.9999998)) #gezev