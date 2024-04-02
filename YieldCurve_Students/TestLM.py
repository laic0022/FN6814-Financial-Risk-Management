from scipy.optimize import leastsq
import numpy as np
import matplotlib.pyplot as plt

def main():
    # data provided
    x = np.array([1.0, 2.5, 3.5, 4.0, 1.1, 1.8, 2.2, 3.7])
    y = np.array([6.008, 15.722, 27.130, 33.772, 5.257, 9.549, 11.098, 28.828])
    # here, create lambda functions for Line, Quadratic fit
    # tpl is a tuple that contains the parameters of the fit
    funcLine = lambda tpl, x : tpl[0]*x+tpl[1]
    funcQuad = lambda tpl, x : tpl[0]*x**2+tpl[1]*x+tpl[2]

    # func is going to be a placeholder for funcLine,funcQuad or whatever
    # function we would like to fit
    func = funcLine

    # ErrorFunc is the difference between the func and the y "experimental" data
    errorFunc = lambda tpl, x, y: func(tpl, x)-y

    # tplInitial contains the "first guess" of the parameters
    tpl_initial1 = (1.0, 2.0)

    # leastsq finds the set of parameters in the tuple tpl that minimizes
    # ErrorFunc=yfit-yExperimental

    tpl_final1, success = leastsq(errorFunc, tpl_initial1[:], args=(x, y))
    print(" linear fit ", tpl_final1)
    xx1 = np.linspace(x.min(), x.max(), 50)
    yy1 = func(tpl_final1, xx1)

    # ------------------------------------------------
    # now the quadratic fit
    # -------------------------------------------------
    func = funcQuad
    tpl_initial2 = (1.0, 2.0, 3.0)
    tpl_final2, success = leastsq(errorFunc, tpl_initial2[:], args=(x, y))
    print("quadratic fit", tpl_final2)
    xx2 = xx1

    yy2 = func(tpl_final2, xx2)
    plt.plot(xx1, yy1, 'r-', x, y, 'bo', xx2, yy2, 'g-')
    plt.show()

class DataStruct(object):
    def __init__(self, param, x, y):
        self.param = param
        self.x = x
        self.y = y
        self.version = 0

    def update_param(self, new_param):
        if new_param is not None and len(self.param) == len(new_param):
            self.param = new_param
            self.version += 1
    def compute_yhat(self):
        y_hat = [self.param[0] * xi ** 2 + self.param[1] * xi + self.param[2] for xi in self.x]
        return y_hat

    def get_y(self):
        return self.y

def func_data(tpl,ds):
    ds.update_param(tpl)
    return ds.compute_yhat() - ds.get_y()

def test_levmar():
    x = np.array([1.0, 2.0, 3.0, 4.0])
    y = np.array([4.0, 15.0, 40.0, 85.0])
    param = np.array([1., 2., 3., 2.])
    funcQuad = lambda tpl, x: tpl[0] * x ** 3 + tpl[1] * x **2 + tpl[2] * x + tpl[3]
    errorFunc = lambda tpl, x, y: funcQuad(tpl, x) - y

    print([funcQuad(param, xi) for xi in x])
    tpl_final2, success = leastsq(errorFunc, param, args=(x, y))
    print("quadratic fit", tpl_final2)
    # print("version", ds.version)

    xx2 = np.linspace(x.min(), x.max(), 50)
    yy2 = funcQuad(tpl_final2, xx2)
    plt.plot(x, y, 'bo', xx2, yy2, 'g-')
    plt.show()

if __name__ == '__main__':
    # main()
    test_levmar()
