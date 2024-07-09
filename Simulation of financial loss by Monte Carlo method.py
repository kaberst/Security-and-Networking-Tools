from scipy.stats import lognorm
from scipy.stats import pareto
import matplotlib.pyplot as plt
import math

def Task2(mu, sigma, xm, alpha, num, point1, point2, point3):
    #generating a list of size num with lognormal random variates
    A = lognorm.rvs(s=sigma, loc=0, scale=math.exp(mu), size=num)
    #generaging a list of size num with rapareto random variates 
    B = pareto.rvs(b=alpha, loc=0, scale=xm, size=num)

    loss_count1 = 0
    loss_count2 = 0
    #checking if the sum of two values from the 2 lists meets the condition
    for i in range (num):
        if(A[i] + B[i] > point1):
            loss_count1 +=1
    #calculating the probability1
    prob1 = loss_count1 / num
    
    #checking if the sum of two values from the 2 lists meets the condition
    for i in range (len(A)):
        if(A[i] + B[i]> point2 and A[i] + B[i] < point3):
            loss_count2 +=1
            
    #calculating the probability
    prob2 = loss_count2 / num
    return (prob1, prob2)

mu = 0
sigma = 5
xm = 1
alpha = 3
num = 50000
point1 = 30
point2 = 50
point3 = 100

prob1, prob2, A, B = Task2(mu, sigma, xm, alpha, num, point1, point2, point3)
