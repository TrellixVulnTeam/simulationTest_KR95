import pyAgrum as gum
import copy as copy
from Experiment import Experiment
from BN import K2_BN, K2_BN_csv_only
import csv
import pandas as pd
import math
import numpy as np
from collections import defaultdict
import csv
import random
import os
import matplotlib.pyplot as plt
import itertools
import shutil
from colour import Color
from CredibilityGame import CredibilityGame
from VlekNetwork import VlekNetwork


def disturb_cpts(path, disturb_type, params_list, file_name):


    if ".net" not in file_name:
        file_name_load = path + file_name + ".net"
    #file_name = "K2BN.net"
    #K2_BN(experiment, "globalStates.csv", file_name)

    #print(file_name)

    org = os.getcwd()
    if experiment.bnDir not in org:
        os.chdir(experiment.bnDir)

    path_bn = path + "/BNs/"+file_name+".net"
    bn1 = gum.loadBN(path_bn)
    bn = gum.BayesNet(bn1)
    noise_list = []


    if disturb_type == "normalNoise":
        '''
        The probabilities in the cpt are not the probabilities generated by K2,
        but they're distorted by a noise error (e)
            X'(X=1) = X(X=1) - e
            X'(X=0) = X(X=0) + e    (or vice versa)

        where e is drawn from a truncatec normal distribution with 
        M = 0, SD = 0.2 (tune parameters later) - the distribution cannot be o . For
        every variable we draw again from this normal distribution.

        This might represent the best case scenario for human estimations
        of probability - even if we cannot know the exact probability,
        we might be able to estimate them closely enough.

        However, it is very likely that our probability estimations
        do not work according to this standard-noise model. For instance,
        racial (or other societal) biases cannot be assumed to 
        be modelled with a "normal" divergence (the noise will be
        predisposed to go into "one direction", and not the other).

        However, first we need to see if BNs are robust against this 
        most simple noise-type of error.

        '''
        m, sd, type = params_list
        smallest_change = 1
        largest_change = 0
        nodes = bn.nodes()  # list of nodes to iterate over (names don't matter because noise is all the same
        for node in list(nodes):
            x = bn.cpt(node)
            name = x.var_names[-1]
            e = np.random.normal(loc=m, scale=sd)
            noise_list.append(e)
            # print(name, e)
            for i in bn.cpt(name).loopIn():
                if i.todict()[name] == 0:
                    bn.cpt(name).set(i, keep_in_range(bn.cpt(name).get(i) + e))
                elif i.todict()[name] == 1:
                    bn.cpt(name).set(i, keep_in_range(bn.cpt(name).get(i) - e))
            if abs(e) > largest_change:
                largest_change = abs(e)
            if abs(e) < smallest_change:
                smallest_change = abs(e)
        # print(largest_change, smallest_change)

        final_file_name = f"{file_name}{disturb_type}BN{str(sd)}"
        gum.saveBN(bn, f"{final_file_name}.net")
        # print(f"saved bn as {file_name}")
        os.chdir(org)
        return [final_file_name, [largest_change, smallest_change]]

    if disturb_type == "rounded":
        ''' we want to round the BN
        to some degree of decimals,
        since humans are not really accurate at 0.0001
        estimations.
        So then we want to get to 0.1, or 0.01 level rounding  (params_list)
        in the network, to see what happens then.
        '''
        [decimal_place, rounded_name] = params_list
        nodes = bn.nodes()  # list of nodes to iterate over (names don't matter because noise is all the same
        for node in list(nodes):
            x = bn.cpt(node)
            name = x.var_names[-1]
            for i in bn.cpt(name).loopIn():
                bn.cpt(name).set(i, round(bn.cpt(name).get(i), decimal_place))

        final_file_name = f"{file_name}{disturb_type}BN{str(decimal_place)}"
        #print("four", final_file_name)
        gum.saveBN(bn, f"{final_file_name}.net")
        return [final_file_name, "empty"]

    if disturb_type == "arbit":
        ''' we want to round the BN
        to some degree (round to quartile, octile, thirds, 2nds, hwatever,
        since we like round numbers

        '''
        #print(path)
        step = params_list
        nodes = bn.nodes()  # list of nodes to iterate over (names don't matter because noise is all the same
        for node in list(nodes):
            x = bn.cpt(node)
            name = x.var_names[-1]
            for i in bn.cpt(name).loopIn():
                val = bn.cpt(name).get(i)
                val = val
                y = math.floor((val / step) + 0.5) * step
                if y == 1:
                    y = 0.99
                if y == 0:
                    y = 0.01
                bn.cpt(name).set(i, y)

        final_file_name = f"{path}/BNs/{file_name}_{disturb_type}_{step}.net"
        #print(final_file_name)
        gum.saveBN(bn, final_file_name)
