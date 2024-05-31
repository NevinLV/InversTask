import math
from itertools import islice

from Receiver import Receiver
from Source import Source


def get_receivers_data():
    receivers = []

    f = open('receivers.txt')

    V_flag = int(f.readline()[0])
    count = int(f.readline())

    for line_number in range(0, count):
        receiver = Receiver()

        if V_flag == 1:
            m1, m2, m3 = f.readline().split(' ')
            receiver.V_true = int(f.readline())
        else:
            m1, m2, m3 = f.readline().split(' ')

        receiver.M.append(int(m1))
        receiver.M.append(int(m2))
        receiver.M.append(int(m3))

        receivers.append(receiver)

    f.close()

    return receivers


def get_source_data():
    AB = []

    n = 0
    file = open('elements.txt')

    I = int(file.readline()[0])
    r1, r2, nr = map(int, file.readline().split())
    z1, z2, nz = map(int, file.readline().split())

    h_r = (r2 - r1) / nr
    h_z = (z2 - z1) / nz

    ksi = []
    eta = []

    for i in range(0, nr + 1):
        ksi.append(r1 + h_r * i)
    ksi[nr] = r2

    for i in range(0, nz + 1):
        eta.append(z1 + h_z * i)
    eta[nz] = z2

    ip = int(file.readline())

    if ip != 0:
        p_list = list(map(float, file.readline().split(' ')))
        for i in range(0, nr * nz):
            source = Source()
            AB.append(source)
            AB[i].p = p_list[i]

    file.close()

    number = 0
    k = 0
    for iz in range(0, nz):
        for ir in range(0, nr):
            AB[k].start_x = ksi[ir]
            AB[k].end_x = ksi[ir + 1]

            AB[k].start_y = eta[iz]
            AB[k].end_y = eta[iz + 1]

            AB[k].A.append((ksi[ir + 1] + ksi[ir]) / 2)
            AB[k].A.append((eta[iz + 1] + eta[iz]) / 2)
            AB[k].A.append(0)
            AB[k].I = I
            AB[k].num = number
            number += 1
            k += 1

    for i in range(0, len(AB)):
        # угловые элементы
        if AB[i].num == 0:  # нижний левый угол
            AB[i].neib.append(1)
            AB[i].neib.append(n)

        if AB[i].num == nr - 1:  # нижний правый угол
            AB[i].neib.append(nr - 2)
            AB[i].neib.append(nr * 2 - 1)

        if AB[i].num == nr * nz - nr:  # верхний левый угол
            AB[i].neib.append(nr * nz - 2 * nr)
            AB[i].neib.append(nr * nz - nr + 1)

        if AB[i].num == nr * nz - 1:  # верхний правый угол
            AB[i].neib.append(nr * nz - nr - 1)
            AB[i].neib.append(nr * nz - 2)

        # элементы нижней строки
        if AB[i].num > 0 and AB[i].num < nr - 1:
            AB[i].neib.append(AB[i].num - 1)
            AB[i].neib.append(AB[i].num + 1)
            AB[i].neib.append(AB[i].num + nr)

        # элементы верхней строки
        if AB[i].num > nr * nz - nr and AB[i].num < nr * nz - 1:
            AB[i].neib.append(AB[i].num - nr)
            AB[i].neib.append(AB[i].num - 1)
            AB[i].neib.append(AB[i].num + 1)

        # 1 column
        if AB[i].num % nr == 0 and AB[i].num != 0 and AB[i].num != nr - 1 and AB[i].num != nr * nz - nr:
            AB[i].neib.append(AB[i].num - nr)
            AB[i].neib.append(AB[i].num + 1)
            AB[i].neib.append(AB[i].num + nr)

        # last column
        if AB[i].num % nr == nr - 1 and AB[i].num != 0 and AB[i].num != nr - 1 and AB[i].num != nr * nz - 1:
            AB[i].neib.append(AB[i].num - nr)
            AB[i].neib.append(AB[i].num - 1)
            AB[i].neib.append(AB[i].num + nr)

        # все остальные элементы
        if len(AB[i].neib) == 1:
            AB[i].neib.append(AB[i].num - nr)
            AB[i].neib.append(AB[i].num - 1)
            AB[i].neib.append(AB[i].num + 1)
            AB[i].neib.append(AB[i].num + nr)

    return AB


def get_r(point1: list, point2: list):
    r = 0.

    if len(point1) != len(point2):
        return -1

    for i in range(0, len(point1)):
        r += (point1[i] - point2[i]) * (point1[i] - point2[i])

    r = math.sqrt(r)
    return r


def getB():
    MN = get_receivers_data()
    AB = get_source_data()

    B = 0.

    for k in range(0, len(MN)):
        MN[k].B = 0
        for i in range(0, len(AB)):
            r2 = pow(get_r(MN[k].M, AB[i].A), 2)
            r3 = pow(get_r(MN[k].M, AB[i].A), 3)
            x_wave = AB[i].A[0] - MN[k].M[0]
            x2 = pow(x_wave, 2)

            mes = AB[i].get_height() * AB[i].get_width()

            B = mes * AB[i].I / (4. * r3 * math.pi) * (AB[i].p * (3. * x2 / r2 - 1.))
            MN[k].B += B

    file = open('B.txt', 'w')

    for k in range(0, len(MN)):
        file.write(f'{MN[k].M[0]} {MN[k].B}\n')

    file.close()

    return MN, AB


def getB_pract(AB: list):
    MN = get_receivers_data()

    for k in range(0, len(MN)):
        MN[k].B = 0
        for i in range(0, len(AB)):
            r2 = pow(get_r(MN[k].M, AB[i].A), 2)
            r3 = pow(get_r(MN[k].M, AB[i].A), 3)
            x_wave = AB[i].A[0] - MN[k].M[0]
            x2 = pow(x_wave, 2)

            mes = AB[i].get_height() * AB[i].get_width()

            B = mes * AB[i].I / (4. * r3 * math.pi) * (AB[i].p * (3. * x2 / r2 - 1.))
            MN[k].B += B

    file = open('inverse_B.txt', 'w')

    for k in range(0, len(MN)):
        file.write(f'{MN[k].M[0]} {MN[k].B}\n')

    file.close()

    return MN, AB
