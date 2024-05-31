import matplotlib.pyplot as plt
import numpy as np

import tools
from Source import Source


def read_true_model(file_name: str):
    x = []
    z = []

    file = open(file_name, 'r')
    for line in file:
        _x, _z = line.split(' ')

        x.append(float(_x))
        z.append(float(_z))

    x.append(float(x[0]))
    z.append(float(z[0]))

    file.close()

    return x, z


def read_point_true_model(file_name: str):
    x_z = []

    file = open(file_name, 'r')
    for line in file:
        _x, _z = line.split(' ')

        x_z.append((float(_x), float(_z)))
    x_z.append(x_z[0])

    file.close()

    return x_z


def write_elements(min_x, max_x, min_z, max_z, split_x, split_z, model_file_name):
    file = open('elements.txt', 'w')
    file.write('1\n')
    file.write(f'{min_x} {max_x} {split_x}\n')
    file.write(f'{min_z} {max_z} {split_z}\n')
    file.write('1\n')

    model_coords = read_point_true_model(model_file_name)

    x_step_size = abs(max_x - min_x) / split_x
    z_step_size = abs(max_z - min_z) / split_z

    z_step = min_z

    p_str = ''

    while z_step <= max_z - z_step_size:
        x_step = min_x
        while x_step <= max_x - x_step_size:
            _x1 = x_step
            _x2 = x_step + x_step_size
            _z1 = z_step
            _z2 = z_step + z_step_size

            is_intersection = False
            for model_coord_i in range(0, len(model_coords) - 1):
                if tools.check_intersection((_x1, _z1, _x2, _z2), model_coords):
                    is_intersection = True

            if is_intersection:
                p_str += '1'
            else:
                p_str += '0'

            p_str += ' '
            x_step += x_step_size
        z_step += z_step_size

    p_str = p_str[:-1]
    file.write(p_str)

    file.close()


def write_receivers(n, start_n, end_n, i):
    length = abs(end_n - start_n)
    step_n = int(length / (n - 1))
    current_n = start_n

    file = open("receivers.txt", "w")
    file.write(f'1\n')
    file.write(f'{n}\n')

    while current_n <= end_n:
        file.write(f'{current_n} {0} {0}\n')
        file.write(f'{i}\n')

        current_n += step_n

    file.close()

def write_F_p(f_p):
    file = open("f_p.txt", "w")
    file.write(f'{f_p}\n')
    file.close()

def write_MN(start, end, count, I):
    file = open("f_p.txt", "w")
    file.write(f'1\n')
    file.write(f'{count}\n')

    length = abs(end - start)
    step = length / count
    current_step = start

    for i in range(0, count):
        file.write(f'{current_step} 0 0\n')
        file.write(f'{I}\n')
        current_step += step
    file.close()


def read_inverse_mesh(nr, nz):
    n = 0

    file = open('Mesh_Inverse.txt', 'r')

    AB = []

    number = 0

    for line in file:
        elem = Source()

        elem.start_x, elem.end_x, elem.start_y, elem.end_y, elem.p = map(float, line.split(' '))

        elem.A.append((elem.end_x + elem.start_x) / 2)
        elem.A.append((elem.end_y + elem.start_y) / 2)
        elem.A.append(0)

        elem.I = 100
        elem.num = number
        number += 1

        AB.append(elem)


    file.close()

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
