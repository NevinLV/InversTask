import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

import IO

def draw_model(receiver_num, AB):
    plt.style.use('default')

    maxx = int(-1200)
    minx = int(1000)

    receivers_x = []
    receivers_z = []
    earth_z = []
    receiver_x_step = abs(minx - maxx) / receiver_num
    current_x = maxx

    while current_x <= minx:
        receivers_x.append(current_x)
        receivers_z.append(10)
        earth_z.append(0)
        current_x += receiver_x_step

    coords = []

    for elem in AB:
        coords.append((elem.start_x, elem.end_x, elem.start_y, elem.end_y, elem.p))

    maxx = int(-1200)
    minx = int(1000)
    maxy = int(30)
    miny = int(-800)
    real = int(1)

    # Get the minimum and maximum function values
    f_vals = [f_val for x_start, x_end, y_start, y_end, f_val in coords]
    f_min, f_max = min(f_vals), max(f_vals)

    # Add the colorbar

    fig, ax = plt.subplots(figsize=(12, 6))

    n_shades = 40
    colors = plt.cm.Greens(np.linspace(0, 1, n_shades))
    cmap = ListedColormap(colors)
    if f_min + 3 < real: f_min = real - 2
    if f_max - 3 > real: f_max = real + 3
    norm = plt.Normalize(vmin=f_min - 0.1, vmax=f_max + 0.1)

    plt.scatter(receivers_x, receivers_z, marker='o', color='#c51010', s=1)
    plt.plot(receivers_x, earth_z, linestyle='-', color='#674800', linewidth=0.5)


    for x_start, x_end, y_start, y_end, f_val in coords:
        if f_val == 0:
            color = '#505050'
        else:
            color = '#10550a'
        rect = plt.Rectangle((x_start, y_start), x_end - x_start, y_end - y_start, linewidth=0.5, edgecolor="#DDDDDD",
                             facecolor=color, alpha=0.5)
        ax.add_patch(rect)

    # Set the axis limits and labels
    ax.set_xlim(maxx, minx)
    ax.set_ylim(miny, maxy)
    ax.set_xlabel("X")
    ax.set_ylabel("Z")

    return fig


def get_solve_b(name):
    f = open(f'B.txt')
    x = []
    y = []

    f2 = open(f'inverse_B.txt')
    x1 = []
    y1 = []

    for line in f2:
        x.append(float(line.split(' ')[0]))
        y.append(float(line.split(' ')[1]))

        x1.append(float(line.split(' ')[0]))
        y1.append(float(line.split(' ')[1]))

    fig, ax = plt.subplots(figsize=(5, 4))


    plt.xlabel("X")
    plt.ylabel("B")

    ax.ticklabel_format(axis='y', scilimits=[0,1])

    ax.set_axisbelow(True)
    plt.grid(True, color='#303030')

    fig.plot(x, y, color='#10550a', marker='o', linewidth=1)
    fig.plot(x1, y1, color='red', marker='<', linewidth=1)

    f.close()
    f2.close()

    return fig

def det_all_b():
    # Считываем координаты из первого файла
    with open('B.txt', 'r') as file:
        data1 = file.readlines()

    x1 = [float(line.split()[0]) for line in data1]
    y1 = [float(line.split()[1]) for line in data1]

    # Считываем координаты из второго файла
    with open('inverse_B.txt', 'r') as file:
        data2 = file.readlines()

    x2 = [float(line.split()[0]) for line in data2]
    y2 = [float(line.split()[1]) for line in data2]

    # Строим график
    plt.scatter(x1, y1, label='File 1')
    plt.scatter(x2, y2, label='File 2')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('График координат')
    plt.legend()
    plt.show()

    return plt.figure

def get_inverse_solve():
    # Read the coordinates and function values from file
    with open("Mesh_Inverse.txt", "r") as f:
        lines = f.readlines()
        coords = [(float(x_start), float(x_end), float(y_start), float(y_end), float(f_val))
                  for x_start, x_end, y_start, y_end, f_val in (line.split() for line in lines)]

        maxx = int(-1200)
        minx = int(1000)
        maxy = int(10)
        miny = int(-800)
        real = int(1)

    # Get the minimum and maximum function values
    f_vals = [f_val for x_start, x_end, y_start, y_end, f_val in coords]
    f_min, f_max = min(f_vals), max(f_vals)

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    plt.style.use('default')

    n_shades = 40
    colors = plt.cm.Greens(np.linspace(0, 1, n_shades))
    cmap = ListedColormap(colors)
    if f_min + 3 < real: f_min = real - 2
    if f_max - 3 > real: f_max = real + 3
    norm = plt.Normalize(vmin=f_min - 0.1, vmax=f_max + 0.1)

    # Loop over the coordinates and plot the rectangles
    for x_start, x_end, y_start, y_end, f_val in coords:
        color = cmap(norm(f_val))
        rect = plt.Rectangle((x_start, y_start), x_end - x_start, y_end - y_start, linewidth=0.5, edgecolor="black",
                             facecolor=color)
        ax.add_patch(rect)

    # Set the axis limits and labels
    ax.set_xlim(maxx, minx)
    ax.set_ylim(miny, maxy)
    ax.set_xlabel("X")
    ax.set_ylabel("Z")

    # Add the colorbar
    scalar_mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(scalar_mappable, ax=ax)

    # Show the plot
    return fig


def show_inverse_solve(num):
    # Read the coordinates and function values from file
    with open(f"Mesh_Inverse{num}.txt", "r") as f:
        lines = f.readlines()
        coords = [(float(x_start), float(x_end), float(y_start), float(y_end), float(f_val))
                  for x_start, x_end, y_start, y_end, f_val in (line.split() for line in lines)]

        maxx = int(-1200)
        minx = int(1000)
        maxy = int(10)
        miny = int(-800)
        real = int(1)

    # Get the minimum and maximum function values
    f_vals = [f_val for x_start, x_end, y_start, y_end, f_val in coords]
    f_min, f_max = min(f_vals), max(f_vals)

    # Set up the figure and axis
    fig, ax = plt.subplots(figsize=(12, 6))

    plt.style.use('default')

    n_shades = 40
    colors = plt.cm.Greens(np.linspace(0, 1, n_shades))
    cmap = ListedColormap(colors)
    if f_min + 3 < real: f_min = real - 2
    if f_max - 3 > real: f_max = real + 3
    norm = plt.Normalize(vmin=f_min - 0.1, vmax=f_max + 0.1)

    # Loop over the coordinates and plot the rectangles
    for x_start, x_end, y_start, y_end, f_val in coords:
        color = cmap(norm(f_val))
        rect = plt.Rectangle((x_start, y_start), x_end - x_start, y_end - y_start, linewidth=0.5, edgecolor="black",
                             facecolor=color)
        ax.add_patch(rect)

    # Set the axis limits and labels
    ax.set_xlim(maxx, minx)
    ax.set_ylim(miny, maxy)
    ax.set_xlabel("Y")
    ax.set_ylabel("Z")

    # Add the colorbar
    scalar_mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(scalar_mappable, ax=ax)

    plt.show()

# show_inverse_solve(1)
# show_inverse_solve(2)
# show_inverse_solve(3)
# show_inverse_solve(4)
# show_inverse_solve(5)
# show_inverse_solve(6)
# show_inverse_solve(7)
# show_inverse_solve(8)
# show_inverse_solve(9)


det_all_b()