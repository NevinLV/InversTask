import copy
import math

import numpy as np
import scipy

import DirectTask
from DirectTask import getB, get_r
from Source import Source
from graphs import draw


def Get_L_matrix(AB: list, MN: list):
    l = 0.
    L = np.full((len(MN), len(AB)), 0.)

    for i in range(0, len(MN)):
        for k in range(0, len(AB)):
            r2 = pow(get_r(MN[i].M, AB[k].A), 2)
            r3 = pow(get_r(MN[i].M, AB[k].A), 3)

            x_wave = AB[k].A[0] - MN[i].M[0]
            x2 = pow(x_wave, 2)

            mes = AB[k].get_height() * AB[k].get_width()

            l = mes * AB[k].I / (4. * r3 * math.pi) * (3. * x2 / r2 - 1.)
            L[i][k] = l

    return L

def WriteMesh_Inverse_bin(AB: list, p):
    file = open('Mesh_Inverse.txt', 'w')
    for _AB, p in zip(AB, p):
        file.write(str(_AB.start_x) + ' ')
        file.write(str(_AB.end_x) + ' ')
        file.write(str(_AB.start_y) + ' ')
        file.write(str(_AB.end_y) + ' ')
        file.write(str(p) + '\n')

    file.close()


def Write_Temp_Mesh_Inverse_bin(AB: list, p, c):
    file = open(f'Mesh_Inverse{c}.txt', 'w')
    for _AB, p in zip(AB, p):
        file.write(str(_AB.start_x) + ' ')
        file.write(str(_AB.end_x) + ' ')
        file.write(str(_AB.start_y) + ' ')
        file.write(str(_AB.end_y) + ' ')
        file.write(str(p) + '\n')

    file.close()


def MatrixC(AB: list, gamma):
    C = np.full((len(AB), len(AB)), 0.)

    for i in range(0, len(AB)):
        for j in range(0, len(AB)):
            if j in AB[i].neib:
                C[i][j] = -(AB[i].gamma + AB[j].gamma)

            if i == j:
                for m in AB[i].neib:
                    C[j][j] = len(AB[i].neib) * AB[i].gamma + AB[m].gamma

    return C

def Functional(MN: list, AB: list, p:list):
    Func = 0.

    _AB = []
    for elem, current_p in zip(AB, p):
        _elem = copy.copy(elem)
        _elem.p = current_p
        _AB.append(_elem)

    _MN, _ = DirectTask.getB_pract(_AB)

    for rec, _rec in zip(MN, _MN):
        Func += pow(rec.B - _rec.B, 2)

    return Func, _AB


def RegFunctional(MN: list, AB: list, p:list, alpha):
    Func, _AB = Functional(MN, AB, p)
    sum_alpha = 0

    for cell in _AB:
        sum_alpha += cell.p**2

    sum_alpha *= alpha

    Func += sum_alpha

    for i in range(0, len(_AB)):
        sum_gamma = 0

        for m in _AB[i].neib:
            sum_gamma += pow(_AB[i].p - _AB[m].p, 2)

        sum_gamma *= _AB[i].gamma
        Func += sum_gamma

    return Func


def solve():
    S = []
    MN, AB = getB()

    for _mn in MN:
        S.append(_mn.B)

    L = Get_L_matrix(AB, MN)
    L_T = L.transpose()

    A = np.dot(L_T, L)

    b = np.dot(L_T, S)

    np.linalg.inv(A) @ b
    p = scipy.linalg.solve(A, b)

    WriteMesh_Inverse_bin(AB, p)
    reg_f_p, _ = Functional(MN, AB, p)

    _AB = []
    for elem, current_p in zip(AB, p):
        _elem = copy.copy(elem)
        _elem.p = current_p
        _AB.append(_elem)

    _MN, _ = DirectTask.getB_pract(_AB)
    return reg_f_p

def reg_solve(alpha, gamma):
    S = []
    MN, AB = getB()

    for _mn in MN:
        S.append(_mn.B)

    L = Get_L_matrix(AB, MN)
    L_T = L.transpose()

    A = np.dot(L_T, L)
    I = np.identity(len(A))
    C = MatrixC(AB, gamma)

    b = np.dot(L_T, S)

    Sum = A + (alpha * I) + C

    np.linalg.inv(Sum) @ b
    p = scipy.linalg.solve(Sum, b)

    WriteMesh_Inverse_bin(AB, p)
    reg_f_p = RegFunctional(MN, AB, p, alpha)
    return reg_f_p

def first_reg_solve(alpha, gamma):
    S = []
    MN, AB = getB()

    for _mn in MN:
        S.append(_mn.B)

    L = Get_L_matrix(AB, MN)
    L_T = L.transpose()

    A = np.dot(L_T, L)
    I = np.identity(len(A))
    C = MatrixC(AB, gamma)

    b = np.dot(L_T, S)

    Sum = A + (alpha * I) + C

    np.linalg.inv(Sum) @ b
    p = scipy.linalg.solve(Sum, b)

    WriteMesh_Inverse_bin(AB, p)
    reg_f_p = RegFunctional(MN, AB, p, alpha)
    return AB, p, reg_f_p


def new_reg_solve(MN: list, AB: list, alpha, gamma, c, first_AB):
    S = []

    for _mn in MN:
        S.append(_mn.B)

    L = Get_L_matrix(AB, MN)
    L_T = L.transpose()

    A = np.dot(L_T, L)
    I = np.identity(len(A))
    C = MatrixC(AB, gamma)

    b = np.dot(L_T, S)

    Sum = A + (alpha * I) + C

    np.linalg.inv(Sum) @ b
    p = scipy.linalg.solve(Sum, b)

    Write_Temp_Mesh_Inverse_bin(AB, p, c)
    WriteMesh_Inverse_bin(AB, p)
    reg_f_p = RegFunctional(MN, first_AB, p, alpha)

    return AB, p, reg_f_p


def search_gamma(alpha, gamma, d_max, d_f_p_max):
    is_first = True

    AB, p, first_f_p = first_reg_solve(alpha, gamma)
    MN, _ = getB()
    c = 0

    _AB = []
    _MN = []

    d_f_p = 0
    while d_f_p < d_f_p_max:
        if not is_first:
            _AB, p, f_p = new_reg_solve(_MN, _AB, alpha, gamma, c, AB)

            for i in range(0, len(_AB)):
                _AB[i].p = p[i]

            d_f_p = f_p / first_f_p
            print(d_f_p)

        else:
            is_first = False

            for elem, current_p in zip(AB, p):
                _elem = copy.copy(elem)
                _elem.p = current_p
                _AB.append(_elem)


        _MN, _ = DirectTask.getB_pract(_AB)

        for i in range(0, len(_AB)):
            for m in _AB[i].neib:
                if _AB[i].p / _AB[m].p > d_max or _AB[m].p / _AB[i].p > d_max:
                    _AB[i].gamma += gamma

        c += 1

    true_f_p, _ = Functional(MN, AB, p)
    return true_f_p


# solve()
# draw()
#
# # reg_solve(10**-11, 10**-9)
# # draw()
