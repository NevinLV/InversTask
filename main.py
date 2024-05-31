import os
import shutil
import sys
from datetime import datetime

import matplotlib
from PyQt6.QtCore import QProcess
from PyQt6.QtGui import QFocusEvent
from PyQt6.QtWidgets import QWidget
from PySide6 import QtGui

import DirectTask
import IO
import draw_graphs
from InverseTask import reg_solve, solve, search_gamma
from graphs import draw_model, draw_true_model, get_solve_b, get_inverse_solve, get_inverse_solve_without_color_map

matplotlib.use('QtAgg')

from PyQt6 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

cellStructStartX = -200
cellStructEndX = 200

cellStructStartZ = -400
cellStructEndZ = -200

cellStructSplitX = 2
cellStructSplitZ = 2

alpha = 1e-6

gamma = 1e-2
max_dp = 10
max_d_f_p = 2

N = 500
start_N = -1000
end_N = 1000
I = 100

value_f_p = 0.

model_file_name = "model.txt"

min_margins = {
    "left": 0.03,
    "bottom": 0.05,
    "right": 0.9,
    "top": 0.990
}

MN, AB = DirectTask.getB()

is_change_cell_param = False

show_plot = "true_model"


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, function_to_call, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor="#232323")
        super(MplCanvas, self).__init__(fig)
        self.function_to_call = function_to_call

    def mousePressEvent(self, event):
        self.function_to_call()


class CellParamQLineEdit(QtWidgets.QLineEdit):
    def __init__(self, function_to_call, parent=None, param=None, var=None):
        super(CellParamQLineEdit, self).__init__(parent)
        self.param = param
        self.var = var
        self.function_to_call = function_to_call

    def focusOutEvent(self, e):
        super(CellParamQLineEdit, self).focusOutEvent(e)

        global cellStructStartX, cellStructEndX, cellStructStartZ, cellStructEndZ, cellStructSplitX, cellStructSplitZ
        global is_change_cell_param

        int_value = int(self.text())

        if self.param == "Начало:":
            if self.var == 'x':
                cellStructStartX = int_value
            elif self.var == 'z':
                cellStructStartZ = int_value

        elif self.param == "Конец:":
            if self.var == 'x':
                cellStructEndX = int_value
            elif self.var == 'z':
                cellStructEndZ = int_value

        elif self.param == "Дробление:":
            if self.var == 'x':
                cellStructSplitX = int_value
            elif self.var == 'z':
                cellStructSplitZ = int_value

        is_change_cell_param = True


class RegParamQLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None, param=None, var=None):
        super(RegParamQLineEdit, self).__init__(parent)
        self.param = param
        self.var = var

    def focusOutEvent(self, e):
        super(RegParamQLineEdit, self).focusOutEvent(e)
        global alpha, gamma, max_dp, max_d_f_p
        int_value = float(self.text())

        if self.param == "α:":
            alpha = int_value
        elif self.param == "+γ:":
            gamma = int_value
        elif self.param == "max dp:":
            max_dp = int_value
        elif self.param == "max dФ(p):":
            max_d_f_p = int_value


class ReceiverParamQLineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None, param=None, var=None):
        super(ReceiverParamQLineEdit, self).__init__(parent)
        self.param = param
        self.var = var

    def focusOutEvent(self, e):
        super(ReceiverParamQLineEdit, self).focusOutEvent(e)

        global N, start_N, end_N, I
        int_value = int(self.text())

        if self.param == "Количество:":
            N = int_value
        elif self.param == "Начало:":
            start_N = int_value
        elif self.param == "Конец:":
            end_N = int_value
        elif self.param == "Мощность:":
            I = int_value


def get_line_param(label: str, value: str):
    param_line = QtWidgets.QHBoxLayout()

    param_line_label = QtWidgets.QLabel(label)
    param_line_label.setStyleSheet("color: #BBBBBB; font-size: 14px; font-family: Arial; font-weight: 100;")
    param_line_label.setFixedSize(230, 25)

    param_line_input = ReceiverParamQLineEdit(value, param=label)
    param_line_input.setStyleSheet(
        "color: #DDDDDD; background-color: #282828; padding: 6px; border: 0px solid #1C6EA4; border-radius: 6px; font-size: 14px; font-family: Arial; font-weight: 100; width: 50px;")
    param_line_input.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
    param_line_input.setFixedSize(80, 25)

    param_line.addWidget(param_line_label)
    param_line.addWidget(param_line_input)

    param_line_widget = QtWidgets.QWidget()
    param_line_widget.setStyleSheet("background-color: #1D1D1D")
    param_line_widget.setFixedSize(320, 35)
    param_line_widget.setLayout(param_line)

    return param_line_widget


def get_line_reg_param(label: str, value: str):
    param_line = QtWidgets.QHBoxLayout()

    param_line_label = QtWidgets.QLabel(label)
    param_line_label.setStyleSheet("color: #BBBBBB; font-size: 14px; font-family: Arial; font-weight: 100;")
    param_line_label.setFixedSize(230, 25)

    param_line_input = RegParamQLineEdit(value, param=label)
    param_line_input.setStyleSheet(
        "color: #DDDDDD; background-color: #282828; padding: 6px; border: 0px solid #1C6EA4; border-radius: 6px; font-size: 14px; font-family: Arial; font-weight: 100; width: 50px;")
    param_line_input.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
    param_line_input.setFixedSize(80, 25)

    param_line.addWidget(param_line_label)
    param_line.addWidget(param_line_input)

    param_line_widget = QtWidgets.QWidget()
    param_line_widget.setStyleSheet("background-color: #1D1D1D")
    param_line_widget.setFixedSize(320, 35)
    param_line_widget.setLayout(param_line)

    return param_line_widget


def get_sruct_grid_line(label, function_to_call, value1, value2):
    param_line = QtWidgets.QHBoxLayout()

    param_line_label = QtWidgets.QLabel(label)
    param_line_label.setStyleSheet("color: #BBBBBB; font-size: 14px; font-family: Arial; font-weight: 100;")
    param_line_label.setFixedSize(200, 25)

    param_line_input1 = CellParamQLineEdit(value1, param=label, var='x')
    param_line_input1.function_to_call = function_to_call
    param_line_input1.setText(value1)
    param_line_input1.setStyleSheet(
        "color: #DDDDDD; background-color: #282828; padding: 6px; border: 0px solid #1C6EA4; border-radius: 5px; font-size: 14px; font-family: Arial; font-weight: 100; width: 50px; margin-right: 20px;")
    param_line_input1.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
    param_line_input1.setFixedSize(85, 25)

    param_line_input2 = CellParamQLineEdit(value2, param=label, var='z')
    param_line_input2.function_to_call = function_to_call
    param_line_input2.setText(value2)
    param_line_input2.setStyleSheet(
        "color: #DDDDDD; background-color: #282828; padding: 6px; border: 0px solid #1C6EA4; border-radius: 5px; font-size: 14px; font-family: Arial; font-weight: 100; width: 50px;")
    param_line_input2.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
    param_line_input2.setFixedSize(65, 25)

    param_line.addWidget(param_line_label)
    param_line.addWidget(param_line_input1)
    param_line.addWidget(param_line_input2)

    param_line_widget = QtWidgets.QWidget()
    param_line_widget.setStyleSheet("background-color: #1D1D1D")
    param_line_widget.setFixedSize(320, 35)
    param_line_widget.setLayout(param_line)

    return param_line_widget


def get_sruct_line_header(label1, label2):
    param_line = QtWidgets.QHBoxLayout()

    param_line_label = QtWidgets.QLabel(' ')
    param_line_label.setStyleSheet("color: #BBBBBB; font-size: 8px; font-family: Arial; font-weight: 100;")
    param_line_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    param_line_label.setFixedSize(200, 15)

    param_line_label1 = QtWidgets.QLabel(label1)
    param_line_label1.setStyleSheet(
        "color: #BBBBBB; background-color: #1D1D1D; font-size: 10px; font-family: Arial; font-weight: 100;")
    param_line_label1.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    param_line_label1.setFixedSize(90, 15)

    param_line_label2 = QtWidgets.QLabel(label2)
    param_line_label2.setStyleSheet(
        "color: #BBBBBB; background-color: #1D1D1D; font-size: 10px; font-family: Arial; font-weight: 100;")
    param_line_label2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
    param_line_label2.setFixedSize(70, 15)

    param_line.addWidget(param_line_label)
    param_line.addWidget(param_line_label1)
    param_line.addWidget(param_line_label2)

    param_line_widget = QtWidgets.QWidget()
    param_line_widget.setStyleSheet("background-color: #1D1D1D")
    param_line_widget.setFixedSize(320, 25)
    param_line_widget.setLayout(param_line)

    return param_line_widget


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.inverse_solve_plot = None
        global cellStructStartX, cellStructEndX, cellStructStartZ, cellStructEndZ, cellStructSplitX, cellStructSplitZ, AB
        global min_margins
        global N, start_N, end_N, I
        global alpha, gamma

        self.program_grid = QtWidgets.QVBoxLayout()
        self.program_widget = QWidget()

        self.main_grid = QtWidgets.QHBoxLayout()
        self.widget = QWidget()

        first_param_title_style = """
            QLabel {
                color: rgb(255, 255, 255); 
                background-color: #1D1D1D; 
                font-size: 14px; 
                font-family: Arial; 
                font-weight: 100;
            }
        """

        param_title_style = """
            QLabel {
                color: rgb(255, 255, 255); 
                background-color: #1D1D1D; 
                font-size: 14px; 
                font-family: Arial; 
                font-weight: 100;
                margin-top: 25px
            }
        """

        # ======================= ПРИЁМНИКИ ================================
        param_label = QtWidgets.QLabel('Приёмники:')
        param_label.setFixedSize(300, 25)
        param_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        param_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        param_label.setStyleSheet(first_param_title_style)

        param_line1_widget = get_line_param("Количество:", str(N))
        param_line2_widget = get_line_param("Начало:", str(start_N))
        param_line3_widget = get_line_param("Конец:", str(end_N))
        param_line4_widget = get_line_param("Мощность:", str(I))

        parameters_grid = QtWidgets.QGridLayout()
        parameters_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        parameters_grid.addWidget(param_label, 0, 0)
        parameters_grid.addWidget(param_line1_widget, 1, 0)
        parameters_grid.addWidget(param_line2_widget, 2, 0)
        parameters_grid.addWidget(param_line3_widget, 3, 0)
        parameters_grid.addWidget(param_line4_widget, 4, 0)
        # ======================================================================

        top_btn_solve_class = """
            QPushButton {
                margin-top: 20px;
                padding: 5px 20px 5px 20px; 
                color: #78cc71; 
                font-size: 12px; 
                border-radius: 14px; 
                background-color: rgb(0,0,0,0);
                border: 1px solid #78cc71;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: #78cc71; 
            }
        """
        btn_solve_class = """
                QPushButton {
                    margin-top: 5px;
                    padding: 5px 20px 5px 20px; 
                    color: #78cc71; 
                    font-size: 12px; 
                    border-radius: 14px; 
                    background-color: rgb(0,0,0,0);
                    border: 1px solid #78cc71;
                }
                QPushButton:hover {
                    color: #ffffff;
                    background-color: #78cc71; 
                }
            """

        # ======================= ЯЧЕИСТАЯ СТРУКТУРА ================================
        struct_param_label = QtWidgets.QLabel('Сетка:')
        struct_param_label.setFixedSize(300, 45)
        struct_param_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        struct_param_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        struct_param_label.setStyleSheet(param_title_style)

        struct_param_line0_widget = get_sruct_line_header("X", "Z")
        struct_param_line1_widget = get_sruct_grid_line(
            "Начало:",
            self.updateCellModel,
            value1=str(cellStructStartX),
            value2=str(cellStructStartZ)
        )

        struct_param_line2_widget = get_sruct_grid_line(
            "Конец:",
            self.updateCellModel,
            value1=str(cellStructEndX),
            value2=str(cellStructEndZ),
        )

        struct_param_line3_widget = get_sruct_grid_line(
            "Дробление:",
            self.updateCellModel,
            value1=str(cellStructSplitX),
            value2=str(cellStructSplitZ),
        )

        build_cell_grid = QtWidgets.QPushButton(text='Построить')

        build_cell_grid.setStyleSheet(top_btn_solve_class)
        build_cell_grid.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        solve_direct_task = QtWidgets.QPushButton(text='Решить прямую задачу')

        solve_direct_task.setStyleSheet(top_btn_solve_class)
        solve_direct_task.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        solve_inverse_task = QtWidgets.QPushButton(text='Решить обратную задачу')
        solve_inverse_task.setStyleSheet(btn_solve_class)
        solve_inverse_task.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

        parameters_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        parameters_grid.addWidget(struct_param_label, 5, 0)
        parameters_grid.addWidget(struct_param_line0_widget, 6, 0)
        parameters_grid.addWidget(struct_param_line1_widget, 7, 0)
        parameters_grid.addWidget(struct_param_line2_widget, 8, 0)
        parameters_grid.addWidget(struct_param_line3_widget, 9, 0)
        parameters_grid.addWidget(build_cell_grid, 10, 0)

        self.reg_checkbox = QtWidgets.QCheckBox("Применить регуляризацию")
        self.reg_checkbox.setStyleSheet("background-color: #1D1D1D; color: white;")

        parameters_grid.addWidget(solve_direct_task, 20, 0)
        parameters_grid.addWidget(solve_inverse_task, 21, 0)
        parameters_grid.addWidget(self.reg_checkbox, 22, 0)

        # ======================================================================

        # ======================= РЕГУЛЯРИЗАЦИЯ ================================
        reg_param_label = QtWidgets.QLabel('Регуляризация:')
        reg_param_label.setFixedSize(300, 40)
        reg_param_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        reg_param_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        reg_param_label.setStyleSheet(param_title_style)

        reg_param_line1_widget = get_line_reg_param("α:", str(alpha))
        reg_param_line2_widget = get_line_reg_param("+γ:", str(gamma))
        reg_param_line3_widget = get_line_reg_param("max dp:", str(max_dp))
        reg_param_line4_widget = get_line_reg_param("max dФ(p):", str(max_d_f_p))

        parameters_grid.addWidget(reg_param_label, 15, 0)
        parameters_grid.addWidget(reg_param_line1_widget, 16, 0)
        parameters_grid.addWidget(reg_param_line2_widget, 17, 0)
        parameters_grid.addWidget(reg_param_line3_widget, 18, 0)
        parameters_grid.addWidget(reg_param_line4_widget, 19, 0)
        # ======================================================================

        parameters_widget = QWidget()
        parameters_widget.setLayout(parameters_grid)
        parameters_widget.setFixedSize(350, 900)

        self.plot_grid = QtWidgets.QVBoxLayout()
        self.plot_widget = QWidget()
        self.plot_widget.setLayout(self.plot_grid)

        self.true_model_label = QtWidgets.QLabel('Истинная модель:')
        self.true_model_label.setContentsMargins(10, 10, 10, 10)
        self.true_model_label.setFixedWidth(1200)
        self.true_model_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.true_model_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.true_model_label.setStyleSheet(
            "color: rgb(255, 255, 255); background-color: #232323; font-size: 16px; font-family: Arial; font-weight: 100;")

        self.sc = MplCanvas(self, width=12, height=4, dpi=100)

        self.mini_plot_1 = MplCanvas(self, width=3, height=2)
        self.mini_plot_2 = MplCanvas(self, width=3, height=2)

        self.mini_plot_3 = MplCanvas(self, width=3, height=2)
        self.mini_plot_4 = MplCanvas(self, width=3, height=2)

        self.main_true_model_figure = draw_true_model(100, model_file_name)
        self.true_model_figure = draw_true_model(100, model_file_name)

        self.main_cell_struct_figure = draw_model(100, AB)
        self.cell_struct_figure = draw_model(100, AB)

        self.sc.figure = self.main_true_model_figure
        self.sc.figure.set_figwidth(5)
        self.sc.figure.set_figheight(4)

        self.mini_plot_1.figure = self.true_model_figure
        self.mini_plot_1.figure.set_facecolor('#212121')

        # self.mini_plot_2.figure = draw_model(100, AB)
        # self.mini_plot_2.figure.set_facecolor('#212121')

        self.mini_plot_1.figure.set_figwidth(3)
        self.mini_plot_1.figure.set_figheight(1)

        self.mini_plot_1.figure.subplots_adjust(**min_margins)

        self.mini_plot_2.figure.set_figwidth(3)
        self.mini_plot_2.figure.set_figheight(1)
        self.mini_plot_2.figure.set_facecolor('#212121')
        self.mini_plot_2.figure.subplots_adjust(**min_margins)

        self.mini_plot_3.figure.set_figwidth(3)
        self.mini_plot_3.figure.set_figheight(1)
        self.mini_plot_3.figure.set_facecolor('#212121')
        self.mini_plot_3.figure.subplots_adjust(**min_margins)

        self.mini_plot_4.figure.set_figwidth(3)
        self.mini_plot_4.figure.set_figheight(1)
        self.mini_plot_4.figure.set_facecolor('#212121')
        self.mini_plot_4.figure.subplots_adjust(**min_margins)

        margins = {
            "left": 0.08,
            "bottom": 0.2,
            "right": 0.9,
            "top": 0.990
        }

        self.sc.figure.subplots_adjust(**margins)

        self.main_graph_box = QtWidgets.QHBoxLayout()
        self.main_graph_box.setSpacing(0)
        self.main_graph_widget = QWidget()
        self.main_graph_widget.setLayout(self.main_graph_box)
        self.main_graph_widget.setFixedHeight(560)

        self.main_graph_widget.setContentsMargins(0, 0, 0, 0)
        self.main_graph_box.setContentsMargins(0, 0, 0, 0)

        self.plot_grid.addWidget(self.true_model_label)

        self.main_graph_box.addWidget(self.sc)

        self.graph_list_box = QtWidgets.QHBoxLayout()
        self.graph_list_widget = QWidget()

        self.graph_list_box.addWidget(self.mini_plot_1)
        self.graph_list_box.addWidget(self.mini_plot_2)

        # self.graph_list_box.addWidget(self.mini_plot_3)
        # self.graph_list_box.addWidget(self.mini_plot_4)

        self.graph_list_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        self.graph_list_widget.setLayout(self.graph_list_box)
        self.graph_list_widget.setFixedHeight(200)
        self.graph_list_widget.setStyleSheet("background-color: #212121; border-top: 1px solid #303030")
        self.graph_list_widget.setContentsMargins(0, 0, 0, 0)

        self.res_line_widget = QWidget()

        self.res_line = QtWidgets.QHBoxLayout()

        btn_simple_class = """
                QPushButton {
                    margin-top: 5px;
                    padding: 5px 20px 5px 20px; 
                    color: #DDDDDD; 
                    font-size: 12px; 
                    border-radius: 14px; 
                    background-color: rgb(0,0,0,0);
                    border: 1px solid #DDDDDD;
                }
                QPushButton:hover {
                    color: #232323;
                    background-color: #DDDDDD; 
                }
            """


        self.open_btn = QtWidgets.QPushButton("Выбрать модель")
        self.open_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.open_btn.setFixedWidth(200)
        self.open_btn.setStyleSheet(btn_simple_class)

        void = QtWidgets.QLabel("")
        void.setStyleSheet(btn_simple_class)
        void.setFixedWidth(550)

        self.save_btn = QtWidgets.QPushButton("Сохранить результаты")
        self.save_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.save_btn.setFixedWidth(200)
        self.save_btn.setStyleSheet(btn_simple_class)

        self.open_folder_btn = QtWidgets.QPushButton("Открыть папку")
        self.open_folder_btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        self.open_folder_btn.setFixedWidth(200)
        self.open_folder_btn.setStyleSheet(btn_simple_class)

        self.open_folder_btn.clicked.connect(self.open_res_folder)
        self.save_btn.clicked.connect(self.save_result)
        self.open_btn.clicked.connect(self.openModelFile)

        self.res_line.addWidget(self.open_btn)
        self.res_line.addWidget(void)
        self.res_line.addWidget(self.open_folder_btn)
        self.res_line.addWidget(self.save_btn)

        self.res_line.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.res_line_widget.setLayout(self.res_line)
        self.res_line_widget.setStyleSheet("background-color: #212121;")

        self.plot_grid.addWidget(self.main_graph_widget, )
        self.plot_grid.addWidget(self.graph_list_widget, )
        self.plot_grid.addWidget(self.res_line_widget, )

        parameters_widget.setObjectName('parameters_panel')
        parameters_widget.setStyleSheet('''
            #parameters_panel{
                background-color: #1D1D1D; border-right: 1px solid #404040;
            }
        '''
        )
        self.main_grid.addWidget(parameters_widget)
        self.main_grid.addWidget(self.plot_widget)
        self.main_grid.setSpacing(0)

        self.program_widget.setLayout(self.main_grid)

        self.program_widget.setStyleSheet("background-color: red")

        solve_direct_task.clicked.connect(self.get_B_plot)
        solve_inverse_task.clicked.connect(self.get_inverse_solve_plot)
        build_cell_grid.clicked.connect(self.updateCellModel)

        self.mini_plot_1.function_to_call = self.show_true_model
        self.mini_plot_2.function_to_call = self.show_cell_model

        self.program_widget.setContentsMargins(0, 0, 0, 0)
        self.program_grid.addWidget(self.program_widget)
        self.program_grid.setSpacing(0)
        self.program_grid.setContentsMargins(0, 0, 0, 0)
        self.widget.setStyleSheet("background-color: red")

        self.widget.setLayout(self.program_grid)

        self.plot_widget.setContentsMargins(0, 0, 0, 0)
        self.main_grid.setContentsMargins(0, 0, 0, 0)
        self.widget.setContentsMargins(0, 0, 0, 0)
        self.plot_grid.setContentsMargins(0, 0, 0, 0)

        self.plot_grid.setSpacing(0)
        self.main_graph_box.setSpacing(0)
        self.graph_list_box.setSpacing(0)
        self.main_grid.setSpacing(0)


        self.setCentralWidget(self.widget)
        self.setWindowTitle('Магниторазведка')

    def open_res_folder(self):
        path = 'results'  # Замените путь на нужный вам
        os.startfile(path)

    def save_result(self):
        global AB

        date = datetime.now().strftime("%d-%m-%Y___%H-%M-%S")
        print(date)
        folder = f'results/{date}'
        os.mkdir(folder)

        shutil.copy('B.txt', f'{folder}/B.txt')
        shutil.copy('elements.txt', f'{folder}/elements.txt')
        shutil.copy('receivers.txt', f'{folder}/receivers.txt')
        shutil.copy('model.txt', f'{folder}/model.txt')
        shutil.copy('Mesh_Inverse.txt', f'{folder}/Mesh_Inverse.txt')
        shutil.copy('f_p.txt', f'{folder}/f_p.txt')

        cell_struct = draw_graphs.draw_model(1000, AB)
        cell_struct.savefig(f'{folder}/Ячеистая структура.png')

        cell_struct = draw_graphs.get_solve_b('B')
        cell_struct.savefig(f'{folder}/B.png')

        cell_struct = draw_graphs.get_solve_b('inverse_B')
        cell_struct.savefig(f'{folder}/inverse_B.png')

        cell_struct = draw_graphs.get_inverse_solve()
        cell_struct.savefig(f'{folder}/Распределение намагниченности.png')


    def openModelFile(self):
        global model_file_name

        fileName, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Выберите файл с моделью",
            "models",
            "*.txt",
        )

        if fileName:
            model_file_name = fileName[0]
            self.main_true_model_figure = draw_true_model(100, model_file_name)

            self.mini_plot_1.deleteLater()
            self.mini_plot_1 = MplCanvas(self, width=3, height=2)
            self.mini_plot_1.figure = draw_true_model(100, model_file_name)
            self.mini_plot_1.function_to_call = self.show_true_model
            self.mini_plot_1.figure.set_facecolor('#212121')
            self.mini_plot_1.figure.set_figwidth(3)
            self.mini_plot_1.figure.set_figheight(1)

            self.mini_plot_1.figure.subplots_adjust(**min_margins)

            self.graph_list_box.replaceWidget(self.mini_plot_2, self.mini_plot_1)

            self.show_true_model()


    def show_true_model(self):
        self.sc.deleteLater()
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.sc.figure = self.main_true_model_figure
        margins = {
            "left": 0.08,
            "bottom": 0.2,
            "right": 0.9,
            "top": 0.990
        }

        self.sc.figure.subplots_adjust(**margins)
        self.main_graph_box.addWidget(self.sc)
        self.true_model_label.setText("Истинная модель:")

    def get_new_B_plot(self):
        global alpha, gamma
        global min_margins
        global N, start_N, end_N, I
        global value_f_p
        global max_d_f_p, max_dp

        IO.write_receivers(N, start_N, end_N, I)

        if (self.reg_checkbox.isChecked()):
            print(alpha, gamma)
            value_f_p = search_gamma(alpha, gamma, max_dp, max_d_f_p)
            IO.write_F_p(value_f_p)
        else:
            value_f_p = solve()

        self.sc.deleteLater()
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.b_plot = get_solve_b("inverse_B")

        self.sc.figure = self.b_plot
        margins = {
            "left": 0.08,
            "bottom": 0.2,
            "right": 0.9,
            "top": 0.95
        }

        self.sc.figure.subplots_adjust(**margins)
        self.main_graph_box.addWidget(self.sc)

        self.mini_plot_3.deleteLater()
        self.mini_plot_3 = MplCanvas(self, width=3, height=2)
        self.mini_plot_3.figure = get_solve_b("inverse_b")
        self.mini_plot_3.function_to_call = self.show_B
        self.mini_plot_3.figure.set_facecolor('#212121')
        self.mini_plot_3.figure.set_figwidth(3)
        self.mini_plot_3.figure.set_figheight(1)

        self.mini_plot_3.figure.subplots_adjust(**min_margins)

        self.graph_list_box.addWidget(self.mini_plot_3)
        self.true_model_label.setText("График B:")

    def get_B_plot(self):
        global alpha, gamma
        global min_margins
        global N, start_N, end_N, I
        global value_f_p
        global max_d_f_p, max_dp

        IO.write_receivers(N, start_N, end_N, I)

        if (self.reg_checkbox.isChecked()):
            print(alpha, gamma)
            value_f_p = search_gamma(alpha, gamma, max_dp, max_d_f_p)
            IO.write_F_p(value_f_p)
        else:
            value_f_p = solve()

        self.sc.deleteLater()
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.b_plot = get_solve_b("B")

        self.sc.figure = self.b_plot
        margins = {
            "left": 0.08,
            "bottom": 0.2,
            "right": 0.9,
            "top": 0.95
        }

        self.sc.figure.subplots_adjust(**margins)
        self.main_graph_box.addWidget(self.sc)

        self.mini_plot_3.deleteLater()
        self.mini_plot_3 = MplCanvas(self, width=3, height=2)
        self.mini_plot_3.figure = get_solve_b("B")
        self.mini_plot_3.function_to_call = self.show_B
        self.mini_plot_3.figure.set_facecolor('#212121')
        self.mini_plot_3.figure.set_figwidth(3)
        self.mini_plot_3.figure.set_figheight(1)

        self.mini_plot_3.figure.subplots_adjust(**min_margins)

        self.graph_list_box.addWidget(self.mini_plot_3)
        self.true_model_label.setText("График B:")

    def show_B(self):
        global alpha, gamma

        self.sc.deleteLater()
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)

        self.sc.figure = self.b_plot
        margins = {
            "left": 0.08,
            "bottom": 0.2,
            "right": 0.9,
            "top": 0.95
        }

        self.sc.figure.subplots_adjust(**margins)
        self.main_graph_box.addWidget(self.sc)
        self.true_model_label.setText("График B:")

    def get_inverse_solve_plot(self):
        global min_margins
        global value_f_p

        self.sc.deleteLater()
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.inverse_solve_plot = get_inverse_solve()

        self.sc.figure = self.inverse_solve_plot
        margins = {
            "left": 0.08,
            "bottom": 0.2,
            "right": 0.9,
            "top": 0.990
        }

        self.sc.figure.subplots_adjust(**margins)
        self.main_graph_box.addWidget(self.sc)

        self.mini_plot_4.deleteLater()
        self.mini_plot_4 = MplCanvas(self, width=3, height=2, dpi=100)

        self.mini_plot_4.figure = get_inverse_solve_without_color_map()
        self.mini_plot_4.figure.set_facecolor('#212121')

        self.mini_plot_4.figure.set_figwidth(3)
        self.mini_plot_4.figure.set_figheight(1)

        self.mini_plot_4.figure.subplots_adjust(**min_margins)
        self.mini_plot_4.function_to_call = self.show_inverse_solve
        self.graph_list_box.addWidget(self.mini_plot_4)
        self.true_model_label.setText(f"Распределение намагниченности в ячеистой структуре (Ф(p) = {value_f_p}):")

        self.get_new_B_plot()

    def show_inverse_solve(self):
        global value_f_p

        self.sc.deleteLater()
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)
        self.sc.figure = self.inverse_solve_plot
        margins = {
            "left": 0.08,
            "bottom": 0.2,
            "right": 0.9,
            "top": 0.990
        }

        self.sc.figure.subplots_adjust(**margins)
        self.main_graph_box.addWidget(self.sc)
        self.true_model_label.setText(f"Распределение намагниченности в ячеистой структуре (Ф(p) = {value_f_p}):")

    def show_cell_model(self):
        global cellStructStartX, cellStructStartZ, cellStructEndX, cellStructEndZ, cellStructSplitX, cellStructSplitZ
        global MN, AB, is_change_cell_param, show_plot

        show_plot = "cell_model"

        self.sc.deleteLater()
        self.sc = MplCanvas(self, width=5, height=4, dpi=100)

        IO.write_elements(cellStructStartX, cellStructEndX, cellStructStartZ, cellStructEndZ, cellStructSplitX,
                          cellStructSplitZ, model_file_name)

        if is_change_cell_param:
            MN, AB = DirectTask.getB()
            self.sc.figure = draw_model(100, AB)
            is_change_cell_param = False
        else:
            self.sc.figure = self.cell_struct_figure

        self.sc.figure.set_facecolor('#232323')
        margins = {
            "left": 0.08,
            "bottom": 0.2,
            "right": 0.9,
            "top": 0.990
        }

        self.sc.figure.subplots_adjust(**margins)
        self.main_graph_box.addWidget(self.sc)
        self.true_model_label.setText("Ячеистая структура:")

    def updateCellModel(self):
        global cellStructStartX, cellStructStartZ, cellStructEndX, cellStructEndZ, cellStructSplitX, cellStructSplitZ
        global MN, AB, is_change_cell_param
        global show_plot
        global min_margins

        is_change_cell_param = True

        if show_plot == "cell_model":
            self.sc.deleteLater()
            self.sc = MplCanvas(self, width=5, height=4, dpi=100)
            IO.write_elements(cellStructStartX, cellStructEndX, cellStructStartZ, cellStructEndZ, cellStructSplitX,
                              cellStructSplitZ)

            MN, AB = DirectTask.getB()
            self.sc.figure = draw_model(100, AB)

        self.mini_plot_2.deleteLater()
        self.mini_plot_2 = MplCanvas(self, width=3, height=2, dpi=100)
        self.mini_plot_2.function_to_call = self.show_cell_model
        IO.write_elements(cellStructStartX, cellStructEndX, cellStructStartZ, cellStructEndZ, cellStructSplitX,
                          cellStructSplitZ, model_file_name)

        MN, AB = DirectTask.getB()
        self.mini_plot_2.figure = draw_model(100, AB)
        self.mini_plot_2.figure.set_facecolor('#212121')

        self.mini_plot_2.figure.subplots_adjust(**min_margins)

        self.mini_plot_2.figure.set_figwidth(3)
        self.mini_plot_2.figure.set_figheight(1)

        margins = {
            "left": 0.08,
            "bottom": 0.2,
            "right": 0.9,
            "top": 0.990
        }

        self.sc.figure.subplots_adjust(**margins)
        self.main_graph_box.addWidget(self.sc)

        self.graph_list_box.addWidget(self.mini_plot_2)
        self.true_model_label.setText("Ячеистая структура:")

    def handler_show_cell_struct(self, state: bool):
        if state:
            self.show_cell_model()
        else:
            self.show_true_model()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()

    screen_width = app.screens()[0].size().width()
    screen_height = app.screens()[0].size().height()

    w.showMaximized()
    w.setContentsMargins(0, 0, 0, 0)
    w.setStyleSheet("background-color: #232323;")

    app.exec()

    # f = search_gamma(alpha, gamma, 10, 0)
    # print(f)


