#!/usr/bin/env python

import array
import random
import sys
from fcntl import flock, LOCK_EX, LOCK_UN, LOCK_NB

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

import math
import time
import random

arq_entrada = '../filtro_terremoto_terra.txt'
name = arq_entrada
t_abertura = 'r'

#@profile
def tabelaFatorial():
    i = 0
    vetor = [0] * 100
    f = open("tabela_fatorial.txt", "r")
    for line in f:
        data = str.split(line)
        vetor[i] = data[1]
        i += 1
    f.close()
    return vetor
    
#@profile
def calc_lat(nome, t_abertura):
    #abre arq
    f = open(nome, t_abertura)
    #x=400, y = 77398

    menor_lat = str(370)
    maior_lat = str(0.0)

    limit_inf = str(34.8)
    limit_sup = str(57.8)

    for line in f:
        data = str.split(line)
        if(data[6] > maior_lat):
            if(data[6] >= limit_sup):
                maior_lat = data[6]

    f.seek(0,0)

    for line in f:
        data = str.split(line) 
        if(data[6] < menor_lat):
            if(data[6] >= limit_inf):
                menor_lat = data[6]
      
    f.close()

    return maior_lat, menor_lat

#@profile
def calc_long(nome, t_abertura):
    f = open(nome, t_abertura)
    #x=400, y = 77398

    menor_long = str(370)
    maior_long = str(0.0)

    limit_inf = str(138.8)
    limit_sup = str(161.8)

    for line in f:
        data = str.split(line)
        if(data[7] > maior_long):
            if(data[7] >= limit_sup):
                maior_long = data[7]

    f.seek(0,0)

    for line in f:
        data = str.split(line) 
        if(data[7] < menor_long):
            if(data[7] >= limit_inf):
                menor_long = data[7]
    
    f.close()
    return maior_long, menor_long

maior_lat, menor_lat = calc_lat(name, t_abertura)
maior_long, menor_long = calc_long(name, t_abertura)

#@profile
def calc_grupo_coord(obs_menor_long, obs_menor_lat, menor_lat, menor_long, var_coord):

    dif_lat = obs_menor_lat - menor_lat
    dif_long = obs_menor_long - menor_long

    # qual_bin_lat = dif_lat / var_coord
    # qual_bin_long = dif_long / var_coord

    primeiro, segundo = 0.5, 1.5
    modificador = divmod(primeiro, 0.5)
    m = modificador[0]
    index = divmod(segundo, 0.5)
    i = index[0]
    indice = i + (m * (dif_lat*dif_long/0.5))

    return int(indice)

#@profile
def cria_vector(total_size, nome, t_abertura, menor_lat, menor_long, var_coord, ano_str):

    f = open(nome, t_abertura)

    N = 0
    N_ano = 0
    total_obs = long(0)

    vector = [None]*(total_size)
    vector_quantidade = [0]*(total_size)
    vector_latlong = [None]*(total_size)
    # kanto region
    for line in f:

        aux2 = str.split(str(line))
        if(int(aux2[0]) == int(ano_str)):
            if(aux2[7] >= 138.8):
                obs_menor_long = float(aux2[7])
            if(aux2[7] >= 34.8):
                obs_menor_lat = float(aux2[6])

            # x_long, y_lat,
            index = calc_grupo_coord(obs_menor_long, obs_menor_lat, menor_lat, menor_long, var_coord)
                    
            vector[index] = line
            vector_quantidade[index] += 1
            N_ano += 1 
        N += 1
        total_obs += 1
    f.close()
    return vector, vector_quantidade, N, total_obs, vector_latlong, len(vector), N_ano

#@profile
def calcular_expectations(modified_quant_por_grupo, total_size, N):

    expectations = [0.0] * (total_size)
    for l in xrange(total_size):
        expectations[l] = (float(modified_quant_por_grupo[l])/float(N))
    return expectations

#@profile
def poisson_press(x,mi):
    if(mi <= 0):
        return
    elif(x >= 0):
        if(x < 1):
            l = math.exp(-mi)
            k = 0
            prob = 1
            while(l < prob):
                k = k + 1
                prob = prob * x
            return (k)
    return 1

#@profile
def calc_coordenadas(var_coord, name, t_abertura):

    # maior_lat, menor_lat = calc_lat(name, t_abertura)
    # maior_long, menor_long = calc_long(name, t_abertura)

    espaco_lat = float(maior_lat) - float(menor_lat)
    espaco_long = float(maior_long) - float(menor_long)

    bins_lat = espaco_lat/var_coord 
    bins_long = espaco_long/var_coord

    bins_lat = round(bins_lat)
    bins_long = round(bins_long)

    return bins_lat, bins_long
#@profile
def dados_observados_R(var_coord, ano_str):

    ##inicio coleta e insercao de incertezas

    #1. Pegar as observacoes e criar o vetor Omega
    #2. Calcular a expectativa das observacoes incertas, vetor de lambdas
    bins_lat, bins_long = calc_coordenadas(var_coord, arq_entrada, 'r')
    
    global menor_lat, menor_long
    menor_lat = float(menor_lat)
    menor_long = float(menor_long)
    bins_lat = int(bins_lat)
    bins_long = int(bins_long)
    total_size = 2025

    # print "inicio da criacao do vetor modificado"

    #3.b) sem modificacao
    modified_vetor, quant_por_grupo, N, total_obs, vector_latlong, total_size, N_ano = cria_vector(total_size, arq_entrada, 'r', 
        menor_lat, menor_long, var_coord, ano_str)

    expectations = calcular_expectations(quant_por_grupo, total_size, N)

    joint_log_likelihood, joint_log_likelihood_NaoUso, descarta_Modelo = log_likelihood(total_size, quant_por_grupo, expectations)

    return joint_log_likelihood, total_size, total_obs, menor_lat, menor_long, vector_latlong, expectations, N_ano, N

#@profile
def log_likelihood(total_size, quant_por_grupo, expectation):

    log_likelihood =  [0]*(total_size)
    joint_log_likelihood = long(0)
    descarta_Modelo = False

    for i in range(total_size):
        if expectation[i] == 0:
            expectation[i] += 1
        # if (quant_por_grupo[i] == 0 and expectation[i] == 0):
        #   log_likelihood[i] += 1      
        # elif (quant_por_grupo[i] != 0 and expectation[i] == 0):
        #   log_likelihood[i] = Decimal('-Infinity')
        #   descarta_Modelo = True
        # else:
            # log_likelihood[i] = -expectation[i] + (quant_por_grupo[i]*math.log10(expectation[i])) - (math.log10(fat(quant_por_grupo[i])))
        if(quant_por_grupo[i] > 100):
            cast = 99
        else:
            cast = quant_por_grupo[i] - 1
        log_likelihood[i] = -expectation[i] + (quant_por_grupo[i]*math.log10(expectation[i])) - (math.log10(float(fatorial[cast])))

    #calcula o joint_log_likelihood
    joint_log_likelihood = sum(log_likelihood)

    return log_likelihood, joint_log_likelihood, descarta_Modelo

total_size = 2025
global mi
mi = 0.0 
global quant_por_grupo
quant_por_grupo = [0] * total_size
global fatorial
fatorial = tabelaFatorial()



creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", array.array, typecode='d', fitness=creator.FitnessMax)

toolbox = base.Toolbox()
# Attribute generator
toolbox.register("attr_float", random.random)
# Structure initializers

toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, total_size)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

#@profile
def evalOneMax(individual):
    global quant_por_grupo
    quant_por_grupo = [0] * len(individual)
    for i in range(len(individual)):
        if(individual[i] < 0):
            individual[i] = -individual[i]
        global quant_por_grupo
        quant_por_grupo[i] = poisson_press(individual[i], mi)

    log_likelihood_ind, log_likelihood_total, descarta_modelo = log_likelihood(total_size, quant_por_grupo, individual)

    # L_test = L_test_sem_correct(joint_log_likelihood, log_likelihood_total, log_likelihood_ind)
    # return L_test,
    return log_likelihood_total,

# Operator registering
toolbox.register("evaluate", evalOneMax)

toolbox.register("mate", tools.cxTwoPoints)

toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)

toolbox.register("select", tools.selRoulette)

fatorial = tabelaFatorial()

def main():
    # random.seed(64)

    CXPB, MUTPB, NGEN = 0.9, 0.1, 100
    ano_int = 1997
    ano_str = str(ano_int)
    
    var_coord = 0.5
    joint_log_likelihood, total_size, total_obs, menor_lat, menor_long, vector_latlong, expectations, N_ano, N = dados_observados_R(var_coord, ano_str)
    global mi
    mi = float(N_ano)/float(N)
    pop = toolbox.population(n=500)

    while(ano_int <= 2013):
        global mi
        mi = float(N_ano)/float(N)
        print("Start of evolution")
        
        # Evaluate the entire population
        fitnesses = list(map(toolbox.evaluate, pop))
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        
        # Begin the evolutionck())
        for g in range(NGEN):
            print("-- Generation %i --" % g)
            # Select the next generation individuals
            offspring = toolbox.select(pop, len(pop))
            # Clone the selected individuals
            offspring = list(map(toolbox.clone, offspring))

            fits = [ind.fitness.values[0] for ind in pop]
            length = len(pop)
            mean = sum(fits) / length
            sum2 = sum(x*x for x in fits)
            std = abs(sum2 / length - mean**2)**0.5
            # Apply crossover and mutation on the offspring
            m = 0
            while (m < 50):
                operator1 = 0
                ja_fez = 0
                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if random.random() < CXPB and ja_fez == 0:
                        toolbox.mate(child1, child2)
                        del child1.fitness.values
                        del child2.fitness.values
                        operator1 = 1
                        m += 2
                        ja_fez = 1
                for mutant in offspring:
                    if(operator1 == 0):
                        if random.random() < MUTPB and ja_fez == 0:
                            toolbox.mutate(mutant, indpb=0.05)
                            del mutant.fitness.values
                            m += 1
                            ja_fez = 1
        # Evaluate the individuals with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            
            print("  Evaluated %i individuals" % len(invalid_ind))
            pop[:] = offspring        
            CXPB, MUTPB = CXPB - (0.003), MUTPB + (0.003)
            # fim loop GERACAO
            joint_log_likelihood, total_size, total_obs, menor_lat, menor_long, vector_latlong, expectations, N_ano, N = dados_observados_R(var_coord, ano_str)
            global mi
            mi = float(N_ano)/float(N)
            
            pop = toolbox.population(n=100)
            fitnesses = list(map(toolbox.evaluate, pop))
            for ind, fit in zip(pop, fitnesses):
                ind.fitness.values = fit

        best_ind = tools.selBest(pop, 1)[0]
        for i in range(len(best_ind)):
            global quant_por_grupo
            quant_por_grupo[i] = poisson_press(best_ind[i], mi)

        while True:
            try:            
                f = open(sys.argv[1], "a")
                flock(f, LOCK_EX | LOCK_NB)
                f.write(str(ano_int))
                f.write('\n')
                for i in range(len(pop)):            
                    f.write(str((pop, 1)[0][i].fitness.values))
                f.write('\n')
                global quant_por_grupo
                f.write(str(quant_por_grupo))
                f.write('\n')
                f.write(str(best_ind.fitness.values))
                f.write('\n')
                flock(f, LOCK_UN)
            except IOError:
                time.sleep(5)
                continue
            break
        CXPB, MUTPB = 0.9, 0.1
        ano_int += 1
        ano_str = str(ano_int)

    elapsed = time.clock()
    print(start - elapsed)
if __name__ == "__main__":
    main()  