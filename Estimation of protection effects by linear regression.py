from scipy.optimize import curve_fit
import numpy as np

def Task3(x, y, num1, num2, num3, num4, bound_y):
    #defining the model of the function used
    def fn(xdata, b0, b1, b2, b3, b4, b5):
        return b0 + b1*xdata[0]+b2*xdata[1]+b3*xdata[2]+b4*xdata[3]+b5*xdata[4]
    #computing weights
    weights, pcov = curve_fit(fn, x, y)
    b0,b1,b2,b3,b4,b5 = weights
    cnt = 0
    num5 = 0
    #generating a num5 that respects the condition
    while cnt < bound_y:
        cnt = b0+b1*num1+b2*num2+b3*num3+b4*num4+b5*num5
        num5 +=1
    num5 -=1
    return (weights, num5)

x = np.array([[5,4,8,8,2,5,5,7,8,8],[3,7,7,2,2,5,10,4,6,3],[8,3,6,7,9,10,6,2,2,3],[9,3,9,3,10,4,2,3,7,5],[4,9,6,6,10,3,8,8,4,6]])
y = np.array([176,170,215,146,228,145,183,151,160,151])
num1, num2, num3, num4, bound_y = 5, 6, 8, 4, 160
result = Task3(x,y, num1, num2, num3, num4, bound_y)
print(result)