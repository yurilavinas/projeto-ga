import random
from calculo_grupos import calc_coordenadas
from calcular_expectations import calcular_expectations
from log_likelihood import log_likelihood
from modificarObservacoes import modificarObservacoes
from cria_vector import cria_vector
from L_test import L_test	
from cria_random import criar_random

##inicio coleta e insercao de incertezas


var_coord = 0.5
# arq_entrada = 'jma_cat_2000_2012_Mth2.5_formatted.dat'
arq_entrada = '../filtro_terremoto_terra.txt'

#1. Pegar as observacoes e criar o vetor Omega
#2. Calcular a expectativa das observacoes incertas, vetor de lambdas
menor_lat, menor_long, bins_lat, bins_long = calc_coordenadas(var_coord, arq_entrada, 'r')

menor_lat = float(menor_lat)
menor_long = float(menor_long)
bins_lat = int(bins_lat)
bins_long = int(bins_long)
total_size = bins_long * bins_lat

print "inicio da criacao do vetor modificado"
#3. Modifica-lo para introduzir incertezas S vezes, gerando um vetor de tamanho S de omega~(modificado). 
random.seed()
s = random.randint(0, 100)

modified_vetor = [None] * s
modified_quant_por_grupo = [0] * s
normalized_mod_quant_grupo = [0] * s
N = [0]*s

for i in range(s):
	modified_vetor[i], modified_quant_por_grupo[i], N[i], total_obs = cria_vector(total_size, arq_entrada, 'r', 
		menor_lat, menor_long, var_coord)

#entra com tamanho do vetor de obs, tamanho do agrupamento e nome do arq e seu mode de abertura
#Calcular expectations
expectations = [0] * s
joint_log_likelihood = [0] * s
descata_modelo = [0] * s

for i in range(s):
	expectations[i] = calcular_expectations(modified_quant_por_grupo[i], total_size, N[i])

	joint_log_likelihood[i], descata_modelo[i] = log_likelihood(total_size, modified_quant_por_grupo[i], expectations[i], total_obs)

##fim coleta e insercao de incertezas

print "Inicio simulacao" 
##simulacao
expectations_simulacao = [0] * s
joint_log_likelihood_simulacao = [0] * s
descata_modelo_simulacao = [0] * s
simulacao_quant_por_grupo = [0] * s

multiplicador = (total_obs/s)/total_size
for i in range(s):
	expectations_simulacao[i], simulacao_quant_por_grupo[i] = criar_random(total_size, N[i], multiplicador, total_obs)
	
	joint_log_likelihood_simulacao[i], descata_modelo_simulacao[i] = log_likelihood(total_size, 
		simulacao_quant_por_grupo[i], expectations_simulacao[i], total_obs)

print 'joint_log_likelihood'	
print joint_log_likelihood
print 'joint_log_likelihood_simulacao'
print joint_log_likelihood_simulacao

#Fazer o calculo do L-test
joint_L_test = L_test(joint_log_likelihood, joint_log_likelihood_simulacao, s)

print 'L_test'
print joint_L_test