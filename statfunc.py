import numpy as np
import scipy as scp
import math
import pandas as pd

def zero_trunc_poisson(obs, lb = None):
    #calcul des probabilités d'observation

    #obs = obs.values #conversion en numpy array
    e = np.average(obs[:,0], axis = 0, weights = obs[:,1]) #espérance de la distribution

    if lb is None:
        lb = lambdacalc(e) #calcul de l'estimateur du facteur de poisson basé sur l'espérance observée

    prob = groupcalc(lb)

    return lb, prob


def lambdacalc(e):
    #calcul du facteur de poisson pour une observation e

    lb0 = 0.1 #facteur de poisson

    def F(x): #fonction objective
        esp = x / (1 - np.exp(-x))
        return np.abs(esp-e)

    lb = scp.optimize.newton_krylov(F, lb0)

    return lb


def groupcalc(lb):
    #calcul des probabilités correspondant au coeff de poisson lb

    prob = np.empty((0, 2))  # initialisation du vecteur des prbabilités de poisson

    for k in range(1,5):
        p = math.pow(lb, k) / ((np.exp(lb)-1)*math.factorial(k))
        prob = np.append(prob, [[k, p]], axis = 0)

    prob = pd.DataFrame(prob, columns = ['Taille', 'Probabilite'])

    return prob