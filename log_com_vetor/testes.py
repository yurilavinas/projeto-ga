# range(0, 10, 3)
# 138.8
# 140.3

# 34.8
# 36.3

# 15000
k, l = 0, 0
x = [0]*45
x[0] = 34.83333333, 138.83333333
x[1] = 34.86666666, 138.86666666 
x[2] = 34.89999999, 138.89999999
x[3] = 34.93333332, 138.83333332
x[4] = 34.96666665, 138.86666665
x[5] = 34.99999998, 138.89999998
x[6] = 35.03333331, 139.03333331
x[7] = 35.06666664, 139.06666664
x[8] = 35.09999997, 139.09999997
x[9] = 35.1333333, 139.1333333
x[10] = 35.16666663, 139.16666663
x[11] = 35.19999996, 139.19999996
x[12] = 35.23333329, 139.23333329
x[13] = 35.26666662, 139.26666662
x[14] = 35.29999995, 139.29999995
x[15] = 35.33333328, 139.33333328
x[16] = 35.36666661, 139.36666661
x[17] = 35.39999994, 139.39999994
x[18] = 35.43333327, 139.43333327
x[19] = 35.4666666, 139.4666666
x[20] = 35.49999993, 139.49999993
x[21] = 35.53333326, 139.53333326
x[22] = 35.56666659, 139.56666659
x[23] = 35.59999992, 139.59999992
x[24] = 35.63333325, 139.63333325
x[25] = 35.66666658, 139.66666658
x[26] = 35.69999991, 139.69999991
x[27] = 35.73333324, 139.73333324
x[28] = 35.76666657, 139.76666657
x[29] = 35.7999999, 139.7999999
x[30] = 35.83333323, 139.83333323
x[31] = 35.86666656, 139.86666656
x[32] = 35.89999989, 139.89999989
x[33] = 35.93333322, 139.93333322
x[34] = 35.96666655, 139.96666655
x[35] = 35.99999988, 139.99999988
x[36] = 36.03333321, 140.03333321
x[37] = 36.06666654, 140.06666654
x[38] = 36.09999987, 140.09999987
x[39] = 36.1333332, 140.1333332
x[40] = 36.16666653, 140.16666653
x[41] = 36.19999986, 140.19999986
x[42] = 36.23333319, 140.23333319
x[43] = 36.26666652, 140.26666652
x[44] = 36.3, 140.3
intervalo = 0.1/3


# loop de inteiros para buscar a posicao das coordenadas no vetor, retorna index (um int)
# o primeiro valor de range e a primeira posicao do vetor, enquanto que o segundo valor, a ultima posicao
# o terceiro indica o incremento a ser feito. Como quero em float, mas range so e para int e tb quero uma
# precisao mais alta, aumentei os valores no range e depois eu faco a divisao, quando quero transformar de
# int para float
for w in range(len(x)):
	for i in range(0, 150000000, 3333333):
		index = float(i)/100000000 + 138.8
		if(x[w][1] >= index and x[w][1] < (index + intervalo)):
			if(index + intervalo > 140.3):
				k -= 1
			break
		k += 1
	for j in range(0, 150000000, 3333333):
		index = float(j)/100000000 + 34.8
		if(x[w][0] >= index and x[w][0] < (index + intervalo)):
			if(index + intervalo > 36.3):
				l -= 1
			break
		l += 1
	print k*45 + l, k, l
	k, l = 0, 0