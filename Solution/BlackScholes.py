import numpy as np

class BlackScholes:
    def __init__(self, s, k, vol, r, maturity, is_call = True):
        if not isinstance(s, np.ndarray):
            self.s = np.array([s])
        else:
            self.s = s
        self.k = k
        self.vol = vol
        self.r = r
        if maturity <= 0:
            raise ValueError('maturity must be greater 0')
        self.maturity = maturity
        self.is_call = is_call

    def d1(self):
        return (np.log(self.s/self.k)+(self.r+0.5*self.vol**2)*self.maturity)/(self.vol*np.sqrt(self.maturity))

    def d2(self):
        return (np.log(self.s/self.k)+(self.r-0.5*self.vol**2)*self.maturity)/(self.vol*np.sqrt(self.maturity))