from scipy.optimize import linprog
import numpy

def Task4(c, safeguard_effect, maintenance_load, se_bound, ml_bound, x_bound, x_initial):
    #creating the inequality constraint matrix
    Aie = [[-x for x in safeguard_effect][1:], maintenance_load]
    #creating the inequality constraint vector
    bie = [-(se_bound - safeguard_effect[0]), ml_bound]
    #creating a list of pairs that represent limits, 
    #defining the minimum and maximum values of the decision variable
    bounds = list()
    for i in range(len(x_bound)):
        b = (x_initial[i],x_bound[i])
        bounds.append(b)
        
    Aeq = None
    beq = None
    #calculating the function result for the entered parameters and 
    #calculating the difference that represents the final result 
    #(how many security controls of each type must be 
    #added to reach the result.x)
    result = linprog(c, Aie, bie, Aeq, beq, bounds)
    x = result.x - x_initial
    return(x)
    

c = [11, 6, 8, 10, 9]
safeguard_effect = [6,3,5,4,8,9]
maintenance_load = [1,2,5,3,3]
se_bound = 1000
ml_bound = 800
x_bound = [30,50,20,45,50]
x_initial = [3,5,4,2,1]
result = Task4(c, safeguard_effect, maintenance_load, se_bound, ml_bound, x_bound, x_initial)
print(result)