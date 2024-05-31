from shapely.geometry import Polygon, box
def is_line_intersect_rectangle(rect, line):
    (R_left, R_top, R_right, R_bottom) = rect
    (L_start, L_end) = line

    # Проверяем, лежит ли один из концов линии внутри прямоугольника
    if (R_left < L_start[0] < R_right and R_top < L_start[1] < R_bottom) or \
            (R_left < L_end[0] < R_right and R_top < L_end[1] < R_bottom):
        return True

# Проверяем пересечение с каждой стороной прямоугольника
    if line_intersects(L_start, L_end, (R_left, R_top), (R_right, R_top)) or \
            line_intersects(L_start, L_end, (R_right, R_top), (R_right, R_bottom)) or \
            line_intersects(L_start, L_end, (R_right, R_bottom), (R_left, R_bottom)) or \
            line_intersects(L_start, L_end, (R_left, R_bottom), (R_left, R_top)):
        return True

    return False

def line_intersects(A, B, C, D):
    # Функция для проверки пересечения двух отрезков AB и CD
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

    return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)

def check_intersection(rect, poly):
    rectangle = box(rect[0] + 0.001, rect[1] + 0.001, rect[2] - 0.001, rect[3] - 0.001)
    polygon = Polygon(poly)
    return rectangle.intersection(polygon)


