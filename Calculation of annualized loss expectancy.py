
def Task1(a, b, c, AV, point1, point2, data):
    #calculating F(x) for x = point1
    if point1 < a:
        pdf1 = 0
        prob1 = 0
    elif point1 < c:
        pdf1 = 2*(point1-a)/((b-a)*(c-a))
        prob1 = ((point1 - a) * pdf1)/2
    elif point1 == c:
        pdf1 = 2/(b-a)
        prob1 = ((point1 - a)*pdf1)/2
    elif point1 <= b:
        pdf1 = 2*(b-point1)/((b-a)*(b-c))
        prob1 = 1 - (((b - point1) * pdf1)/2)
    else:
        prob1 = 0

    #calculating F(x) for x = point2
    if point2 < a:
        pdf2 = 0
        prob2 = 0
    elif point2 < c:
        pdf2 = 2*(point2-a)/((b-a)*(c-a))
        prob2 =  1 - (((point2 - a)*pdf2)/2)
    elif point2 == c:
        pdf2 = 2/(b-a)
        prob2 = ((b-point2)*pdf2)/2
    elif point2 <= b:
        pdf2 = 2*(b-point2)/((b-a)*(b-c))
        prob2 = ((b-point2)*pdf2)/2
    else:
        prob2 = 0

    
    
    mean_tr = (a+b+c) / 3
    #using the mean as SLE
    SLE = mean_tr
    #calculating the EF
    EF = SLE / AV
    #calculating mean of data set
    mean = sum(data) / len(data)
    #calculating variance
    v_data = [(x-mean)**2 for x in data]
    variance = sum(v_data) / len(data)
    #calculating the value of ALE
    ALE = mean * SLE


    return (prob1, prob2, EF, mean, variance, ALE)

a = 1000
b = 10000
c = 4000
AV = 10000
point1 = 2000
point2 = 8000
data = [5, 7, 3, 9, 7, 4, 5, 6, 8, 2]

result = Task1(a,b,c,AV,point1,point2,data)
print(result)