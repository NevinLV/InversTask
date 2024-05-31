class Source:
    A = []
    B = []
    I = 0.
    I_prev = 0.
    p = 0.
    start_x = 0.
    start_y = 0.
    end_x = 0.
    end_y = 0.
    gamma = 0.

    num = 0
    neib = []

    def __init__(self):
            self.A = []
            self.B = []
            self.I = 0.
            self.I_prev = 0.
            self.p = 0.
            self.start_x = 0.
            self.start_y = 0.
            self.end_x = 0.
            self.end_y = 0.
            self.gamma = 1e-18

            self.num = 0
            self.neib = []

    def get_height(self):
        return self.end_x - self.start_x

    def get_width(self):
        return self.end_y - self.start_y


