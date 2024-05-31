import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

from DirectTask import get_source_data
import IO


def draw():
    f = open('B.txt')
    x = []
    y = []

    for line in f:
        x.append(float(line.split(' ')[0]))
        y.append(float(line.split(' ')[1]))

    plt.plot(x, y)
    plt.show()

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
    fig, ax = plt.subplots(figsize=(5, 4))

    n_shades = 40
    colors = plt.cm.Oranges(np.linspace(0, 1, n_shades))
    cmap = ListedColormap(colors)
    if f_min + 3 < real: f_min = real - 2
    if f_max - 3 > real: f_max = real + 3
    norm = plt.Normalize(vmin=f_min - 0.1, vmax=f_max + 0.1)

    # Loop over the coordinates and plot the rectangles
    for x_start, x_end, y_start, y_end, f_val in coords:
        color = cmap(norm(f_val))
        rect = plt.Rectangle((x_start, y_start), x_end - x_start, y_end - y_start, linewidth=1, edgecolor="black",
                             facecolor=color)
        ax.add_patch(rect)

    # Set the axis limits and labels
    ax.set_xlim(maxx, minx)
    ax.set_ylim(miny, maxy)
    ax.set_xlabel("Y")
    ax.set_ylabel("Z")

    # Add the colorbar
    scalar_mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    cbar = fig.colorbar(scalar_mappable, ax=ax, label="p values")

    # Show the plot
    plt.show()


def draw_model(receiver_num, AB):
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

    # Set up the figure and axis
    plt.style.use('dark_background')
    # Add the colorbar

    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#232323')
    ax.set_facecolor("#232323")

    ax.set_axisbelow(True)
    plt.grid(True, color='#303030')

    n_shades = 40
    colors = plt.cm.Greens(np.linspace(0, 1, n_shades))
    cmap = ListedColormap(colors)
    if f_min + 3 < real: f_min = real - 2
    if f_max - 3 > real: f_max = real + 3
    norm = plt.Normalize(vmin=f_min - 0.1, vmax=f_max + 0.1)

    plt.scatter(receivers_x, receivers_z, marker='o', color='#df5050', s=1)
    plt.plot(receivers_x, earth_z, linestyle='-', color='#f2ec85', linewidth=0.5)

    # Loop over the coordinates and plot the rectangles
    for x_start, x_end, y_start, y_end, f_val in coords:
        if f_val == 0:
            color = '#505050'
        else:
            color = '#76ea9a'
        rect = plt.Rectangle((x_start, y_start), x_end - x_start, y_end - y_start, linewidth=0.5, edgecolor="#DDDDDD",
                             facecolor=color, alpha=0.5)
        ax.add_patch(rect)

    # Set the axis limits and labels
    ax.set_xlim(maxx, minx)
    ax.set_ylim(miny, maxy)
    ax.set_xlabel("X")
    ax.set_ylabel("Z")

    return fig


def draw_true_model(receiver_num: int, file_name: str):
    x, z = IO.read_true_model(file_name)

    maxx = int(-1200)
    minx = int(1000)
    maxy = int(30)
    miny = int(-800)

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

    # Set up the figure and axis
    plt.style.use('dark_background')
    # Add the colorbar

    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#232323', alpha=0)
    ax.set_facecolor("#232323")

    ax.set_axisbelow(True)
    plt.grid(True, color='#303030')

    # Рисуем многоугольник
    plt.scatter(receivers_x, receivers_z, marker='o', color='#df5050', s=1)
    plt.plot(receivers_x, earth_z, linestyle='-', color='#f2ec85', linewidth=0.5)
    plt.plot(x, z, linestyle='-', color='#76ea9a')

    # Заливаем внутреннюю часть многоугольника цветом
    plt.fill(x, z, color='#76ea9a', alpha=0.5)

    # Set the axis limits and labels
    ax.set_xlim(maxx, minx)
    ax.set_ylim(miny, maxy)
    ax.set_xlabel("X")
    ax.set_ylabel("Z")

    return fig

def get_solve_b(name):
    f = open(f'{name}.txt')
    x = []
    y = []

    for line in f:
        x.append(float(line.split(' ')[0]))
        y.append(float(line.split(' ')[1]))

    plt.style.use('dark_background')

    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#232323', alpha=0)

    plt.xlabel("X")
    plt.ylabel("B")

    ax.set_facecolor("#232323")
    ax.ticklabel_format(axis='y', scilimits=[0,1])

    ax.set_axisbelow(True)
    plt.grid(True, color='#303030')
    plt.plot(x, y, color='#76ea9a', linewidth=1)

    f.close()

    return fig

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
    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#232323', alpha=0)
    ax.set_facecolor('#232323')

    ax.set_axisbelow(True)
    plt.grid(True, color='#303030')

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


def get_inverse_solve_without_color_map():
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
    fig, ax = plt.subplots(figsize=(5, 4), facecolor='#232323', alpha=0)
    ax.set_facecolor('#232323')

    ax.set_axisbelow(True)
    plt.grid(True, color='#303030')

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


    # Show the plot
    return fig



