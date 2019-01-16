import numpy as np
import pandas as pd
import math
import statfunc

def calibrage(x, t = 1, lp = None, seuil = 140):
    '''
    Calibrage des débits piétons

    :param x: débits piétons
    :param t: durée des périodes de comptage en heures, par défaut 1 heure. Peut prendre des valeurs décimales (ex: périodes de 15 min, t = 0.25)
    :param lp: facteur de poisson pour expliquer la distribution des groupes
    :param seuil: valeur seuil pour le débit/t à partir de laquelle la correction est nécessaire. par défaut: 180 p/heure
    :return: débits corrigés
    '''

    if lp is None:
        lp = 0.20478090122525708 * t / 0.5  #valeur de lp pour 30 minutes rapportée à la durée totale

    prob = statfunc.groupcalc(lp) #probabilité d'avoir des groupes
    deblist = []

    if np.isscalar(x):
        if x >= seuil * t:
            deblist = x*(1 + prob.iloc[1]['Probabilite'] + 0.5*prob.iloc[2]['Probabilite'])
    else:

        for deb in x:
            if deb >= seuil * t:
                new_deb = deb * (1 + prob.iloc[1]['Probabilite'] + 0.5*prob.iloc[2]['Probabilite'])
                deblist.append(new_deb)
            else:
                deblist.append(deb)

    x_corr = deblist

    return x_corr

def err_rel(x1, x2):
    '''
    Calcule l'erreur relative entre deux inputs x1 et x2
    '''

    err = []

    if np.isscalar(x1) and np.isscalar(x2):
        e = (x1 - x2)/x1
        err = e

    elif not(np.isscalar(x1)) and not(np.isscalar(x2)):

        for a, b in zip(x1, x2):

            e = (b-a)/a
            err.append(e)

        else:
            print('Erreur de format')
            return

    return err

def rmse(x1, x2):
    '''
    Calcule l'erreur quadratique moyenne entre deux inputs x1 et x2
    '''

    e = 0
    n = 0

    if np.isscalar(x1) and np.isscalar(x2):
        e = (x2 - x1)**2
        n = 1

    elif not(np.isscalar(x1)) and not(np.isscalar(x2)):

        for a, b in zip(x1, x2):
            e += (b-a)**2
            n += 1

        else:
            print('Erreur de format')
            return


    err = np.sqrt(e/n)

    return err


