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






def determine_winning_hypothesis(false_val, true_val):
    x = ""
    if false_val > true_val:
        x = "H0"
    elif false_val < true_val:
        x = "H1"
    else:
        x = "0"
    return x

def find_posterior_based_on_evidence():
    pass

def get_evidence_list():
    '''
    evidence needs to be added in the correct order
     this is determined by the investigator,
     and the order is determined in this function.
     '''
    evidence_order = []
    if experiment.scenario == "StolenLaptop":
        evidence_order = ["E_object_is_gone", "E_broken_lock", "E_disturbed_house", "E_s_spotted_by_house", "E_s_spotted_with_goodie", "E_private"]
    elif experiment.scenario == "CredibilityGame":
        for i in range(0, experiment.n):
            str1 = f"E_{i}_says_stolen"
            # str2 = i + "_credibility"
            evidence_order.append(str1)
    return evidence_order


def determine_posterior_direction_or_precision(dir, file_name, direction):  # type is 'direction' or 'precision
    #if file_name != "BayesNets/K2BN.net":
    #    bn = gum.loadBN(f"{file_name}.net")
    #else:


    #print("file_name", file_name)
    if "net" not in file_name:
        file_name = file_name + ".net"

    org_dir = os.getcwd()
    #print(org_dir)


    if dir not in os.getcwd():
        os.chdir(dir)

    bn = gum.loadBN(file_name)
    os.chdir(org_dir)

    direction_dict = {}
    ie = gum.LazyPropagation(bn)
    event_list = list(bn.names())#experiment.reporters.relevant_events
    e_dict = {}
    for node in list(bn.names()):
        x = bn.cpt(node)
        name = x.var_names[-1]
        if name[0] != 'E':  # we do not care about evidence nodes
            if direction == "weak":
                e_dict[name] = determine_winning_hypothesis(ie.posterior(node)[0], ie.posterior(node)[1]) # compare the posteriors (false, true) for node "name"
            elif direction == "strong":  # we just want to know the posterior for truth of a node
                e_dict[name] = round(ie.posterior(node)[1], 2)
                #print(name, e_dict[name])

    direction_dict[("no_evidence", 0)] = e_dict

    evidence_list = get_evidence_list()

    for evidence in evidence_list:
        e_dict = {}
        if evidence != "E_private":
            val = 1
        else:
            val = 0
        ie.addEvidence(evidence, val)
        #print(evidence, val)

        for node in list(bn.nodes()):
            x = bn.cpt(node)
            name = x.var_names[-1]
            if name[0] != 'E':  # we do not care about evidence nodes
                try:
                    if direction == "weak":
                        e_dict[name] = determine_winning_hypothesis(ie.posterior(node)[0], ie.posterior(node)[1])
                    else:
                        e_dict[name] = round(ie.posterior(node)[1], 2)
                        #print("\t", name, e_dict[name])

                except:
                    e_dict[name] = "NA"


        direction_dict[(evidence, val)] = e_dict

    return direction_dict

def keep_in_range(x):
    ''' numbers in a ctp cannot be > 1 or < 0'''
    if x > 1:
        return 1
    if x < 0:
        return 0
    return x

def make_table_headings_based_on_events(relevant_events):
    str_tabular_formatting = "\\begin{tabular}{l"
    for i in range(0, len(relevant_events)):
        str_tabular_formatting = str_tabular_formatting + "|cc"
    str_tabular_formatting = str_tabular_formatting + "}"

    str_head = "\\multirow{2}{*}{Evidence} "
    for e in relevant_events:
        l_key = e.replace("_", " ")
        str_head = str_head + "& \\multicolumn{2}{c}{" + l_key + "}"
    str_head = str_head + "\\\\"

    for e in relevant_events:
        str_head = str_head + "& {K2} & {Dev}"
    str_head = str_head + "\\\\"
    return str_tabular_formatting, str_head



def get_outcomes_in_table(d1, d_noise, latex_file_name, params, direction, noise, relevant_events):  # compare two direction dictionaries
    tab_f, head_f = make_table_headings_based_on_events(relevant_events)
    if len(relevant_events) > 3:
        outcomes = "outcomes"
    else:
        outcomes = "hypotheses"

    with open(latex_file_name, 'w') as file:
        file.write("\\begin{table}")
        file.write(tab_f)
        file.write("\\toprule")
        file.write(head_f)
        file.write("\\midrule\n")

        for e in d1.keys():
            l_key = e[0].replace("_", " ")
            file.write(str(l_key) + ", " + str(e[1]) + " & ")
            for x in relevant_events:
                if direction == "weak":
                    if not noise:   # if not noise
                        d2 = d_noise

                        if d1[e][x] == d2[e][x]:
                            file.write(str(d1[e][x]) + "&" + str(d2[e][x]))
                        else:
                            file.write(
                                "\\cellcolor{Bittersweet}" + str(d1[e][x]) + "&" + "\\cellcolor{Bittersweet}" + str(
                                    d2[e][x]))
                    else:   #if noise
                        count = 0
                        for d2 in d_noise:
                            if d1[e][x] == d2[e][x]:
                                count += 1
                        if (count / len(d_noise)) < 0.95:
                            file.write("\\cellcolor{Bittersweet}" + str(d1[e][x]) + "&" + "\\cellcolor{Bittersweet}" + str(
                                round(100 * (count / len(d_noise)), 0)))
                        else:
                            file.write(str(d1[e][x]) + "&" + str(round(100 * (count / len(d_noise)), 0)))
                if direction == "strong":
                    if not noise:   # something number of nodes
                        d2 = d_noise
                        if type(d2[e][x]) == float and abs(d1[e][x] - d2[e][x]) < 0.05:
                            file.write(str(d1[e][x]) + "&" + str(d2[e][x]))
                        else:
                            file.write(
                                "\\cellcolor{Bittersweet}" + str(d1[e][x]) + "&" + "\\cellcolor{Bittersweet}" + str(
                                    d2[e][x]))
                    else: # noise randomness precisison
                        count = 0
                        for d2 in d_noise:
                            if type(d2[e][x]) == float and d2[e][x] != "NA":
                                count += d2[e][x]
                            else:
                                count += 0.5
                        if abs(d1[e][x] - (count / len(d_noise))) > 0.05:
                            file.write("\\cellcolor{Bittersweet}" + str(d1[e][x]) + "&" + "\\cellcolor{Bittersweet}" + str(
                                round((count / len(d_noise)), 0)))
                        else:
                            t = round((count / len(d_noise)), 0)
                            file.write(str(d1[e][x]) + "&" + str(t))

                if x != relevant_events[-1]:
                    file.write("&")
            file.write("\\\\")

        file.write("\\bottomrule")
        file.write("\\end{tabular}")
        file.write("\\caption{Effect of disturbance of " + str(params) + " on " + str(direction) + " view of " + str(outcomes) + ".}")
        file.write("\\end{table}")

def get_relevant_hyp_events(bnDir, org_BN, outcome_nodes):


    if ".net" not in org_BN:
        org_BN =  org_BN + ".net"
    os.chdir(bnDir)
    bn = gum.loadBN(org_BN)
    hyp_nodes = []
    for x in bn.names():
        if x not in outcome_nodes and x[0] != 'E':
            hyp_nodes.append(x)

    return hyp_nodes



def experiment_general_shape(main_exp, type_exp, org_BN, param_list, general_latex_file, experiment_list, test_set, analysis):

    # reset dir
    org_dir = os.getcwd()
    #print(main_exp.scenario)
    d_2 = []
    noise = False
    relevant_files = []
    if main_exp.scenario == "StolenLaptop":
        relevant_nodes_out = ["successful_stolen", "lost_object"]
        relevant_nodes_hyp = get_relevant_hyp_events(main_exp.bnDir, org_BN, relevant_nodes_out) #["curtains", "raining", "know_object", "target_object", "motive", "compromise_house", "flees_startled"]
    elif main_exp.scenario == "CredibilityGame":
        relevant_nodes_out = ["agent_steals"]
        relevant_nodes_hyp = get_relevant_hyp_events(main_exp.bnDir, org_BN, relevant_nodes_out) # no hyps here
    elif main_exp.scenario == "VlekNetwork":
        relevant_nodes_out = ["mark_dies"]
    elif main_exp.scenario == 2:
        relevant_nodes_out = ["stealing_1_0"]
        #relevant_nodes_hyp = get_relevant_hyp_events(main_exp.bnDir, org_BN, relevant_nodes_out)  # no hyps here

    # establish original BN
    analysis.output_nodes = relevant_nodes_out
    acc, rms = calculate_accuracy(org_BN, test_set, relevant_nodes_out, org_dir, main_exp.bnDir, analysis, "first")

    for direc in ["weak", "strong"]:
        d_1 = determine_posterior_direction_or_precision(main_exp.bnDir, org_BN, direc)
        for a in d_1.keys():
            for b in d_1[a].keys():
                experiment_list.append(["K2", 0, direc, 0, a[0] + str(a[1]), b, d_1[a][b], d_1[a][b], acc, rms])

    for params in param_list:
        [disturbed_BN_file_name, empty] = disturb_cpts(experiment, type_exp, params, org_BN)
        acc, rms = calculate_accuracy(disturbed_BN_file_name, test_set, relevant_nodes_out, org_dir,  main_exp.bnDir, analysis, "not first")

        for direc in ["weak", "strong"]:
            if type_exp == "normalNoise":
                for i in range(0, 200):
                    noise = True
                    d_i = determine_posterior_direction_or_precision(main_exp.bnDir, disturbed_BN_file_name, direc)
                    d_2.append(d_i)

                    for a in d_i.keys():
                        for b in d_i[a].keys():
                            experiment_list.append([type_exp, params[1], direc, i, a[0]+str(a[1]), b, d_i[a][b], d_1[a][b], acc, rms])

            else:
                [disturbed_BN_file_name, empty] = disturb_cpts(experiment, type_exp, params, org_BN)
                #print(disturbed_BN_file_name)
                d_2 = determine_posterior_direction_or_precision(main_exp.bnDir, disturbed_BN_file_name, direc)
                for a in d_2.keys():
                    for b in d_2[a].keys():
                        experiment_list.append([type_exp, params[0], direc, 0, a[0]+str(a[1]), b, d_2[a][b], d_1[a][b], acc, rms])

            os.chdir(org_dir)
            outcome_table = f'texTables/outcome/{direc}{disturbed_BN_file_name}.tex'
            hyp_table = f'texTables/hyps/{direc}{disturbed_BN_file_name}.tex'


            #get_outcomes_in_table(d_1, d_2, outcome_table, params, direc, noise, relevant_nodes_out)
            #get_outcomes_in_table(d_1, d_2, hyp_table, params, direc, noise, relevant_nodes_hyp)


            relevant_files.append(outcome_table)
            relevant_files.append(hyp_table)


    # output of experiment
    with open(general_latex_file, 'w') as file:
        for f in relevant_files:
            file.write("\\input{../simulationTest/" + f + "}\n")


def hugin_converter(bnfilename, path):  # make the network handable in hugin with some cheats
    bn = path + "/BNs/"+bnfilename+".net"
    file1 = open(bn, 'r')
    Lines = file1.readlines()
    count = 0
    # Strips the newline character
    proper = []
    for line in Lines:
        count += 1
        flag = 0
        for x in ["unnamedBN;", "aGrUM 0.22.5", "node_size"]:
            if x in line:
                flag = 1

        if flag == 0:
            if "states = (0 1 );" in line:
                line = "states = (\"0\" \"1\");\n"
            elif "states = (1 0 );" in line:
                line = "states = (\"1\" \"0\");\n"
            #print("Line{}: {}".format(count, line))
            proper.append(line)

    #print(bnfilename)

    with open(path+"/huginBN/"+bnfilename+".net", 'w') as file2:
        file2.writelines(proper)


def calculate_accuracy(network, test_set, output_nodes, orgDir, bnDir, analysis, first):
    '''print(network)
    print(orgDir)
    print(bnDir)
    print(os.getcwd())'''
    print(network)

    if "net" not in network:
        network = network + ".net"

    #org_dir = orgDir
    #if dir not in os.getcwd():
    os.chdir(analysis.network_dir)

    bn = gum.loadBN(network)
    os.chdir(analysis.org_dir)

    # todo: set evidence
    # see value of output
    # if the same +1, else +0
    # then calcualte accuracy
    # store D in some other array

    direction_dict = {}
    event_list = list(bn.names())  # experiment.reporters.relevant_events
    evidence = []
    for x in event_list:
        if x[0] == "E": # evidence node
            evidence.append(x)



    df = pd.read_csv(analysis.test_csv, sep=r',',
            skipinitialspace = True)

    accuracy = 0
    rmsd = 0
    #print(output_nodes)
    network_name = []
    pred_output=[]
    matching_output=[]
    rms_list=[]
    input_list = []
    output_list = []
    for i in range(0, len(df)):
        ie = gum.LazyPropagation(bn)
        k = []
        for ev in evidence:
            val = df.loc[i, ev]
            ie.addEvidence(ev, int(val))
            k.append(val)

        for output_node in output_nodes:
            val_output = df.loc[i, output_node]
            output_list.append(val_output)
            #print("output actual",val_output)
            try:
                fin = round(ie.posterior(output_node)[1], 2)
                rmsd += round(abs(fin - val_output), 2)
                rms_list.append(round(abs(fin - val_output), 2))

            except:
                fin = "NA"
                rmsd += 1
                rms_list.append(1)

            if fin == val_output:
                accuracy += 1
                matching_output.append(1)
            else:
                matching_output.append(0)

                pass

            pred_output.append(fin)
            network_name.append(network)
            input_list.append(k)

    otp = {}
    otp["network"] = network_name
    otp["input"] = input_list
    otp["output"] = output_list
    otp["predicted"] = pred_output
    otp["matching"] = matching_output
    otp["RMS"] = rms_list
    otp_pd = pd.DataFrame.from_dict(otp)

    if first == "first":
        otp_pd.to_csv(analysis.accuracy_csv, index=False)
    else:
        otp_pd.to_csv(analysis.accuracy_csv, index=False, mode='a', header=False)





                #print(fin, val_output)


    #print("\t final accuracy in posterior", accuracy/(len(output_nodes) * len(df)))
    #print("\t rmsd", rmsd/(len(output_nodes) * len(df)))
    return accuracy/(len(output_nodes) * len(df)), rmsd/(len(output_nodes) * len(df))

def calculate_accuracy_1(file_name, path):
    '''print(network)
    print(orgDir)
    print(bnDir)
    print(os.getcwd())'''


    network = path + "/BNs/"+file_name+".net"
    if "param" not in file_name and "map" not in file_name:
        csv_name = file_name.split("_", 1)[0]   # we want to refer to hte original csv file
    else:
        csv_name = file_name


    csv_file = path + "/test/"+csv_name+".csv"


    if "net" not in network:
        network = network + ".net"

    #org_dir = orgDir
    #if dir not in os.getcwd():


    bn = gum.loadBN(network)

    # todo: set evidence
    # see value of output
    # if the same +1, else +0
    # then calcualte accuracy
    # store D in some other array

    direction_dict = {}


    '''evidence = []
    for x in event_list:
        if x[0] == "E": # evidence node
            evidence.append(x)
    '''





    df = pd.read_csv(csv_file, sep=r',',
            skipinitialspace = True)

    #print(df.columns)

    accuracy = 0
    rmsd = 0
    #print(output_nodes)
    network_name = []
    pred_output=[]
    matching_output=[]
    rms_list=[]
    output_list = []
    name_output_list = []
    rounded_predicted_output = []
    for i in range(0, len(df)):
        #print("NEW COMBO")
        event_list = list(bn.names())  # experiment.reporters.relevant_events
        random.shuffle(event_list)
        output_node = event_list.pop()

        ie = gum.LazyPropagation(bn)
        val_output = df.loc[i, output_node]

        #print("going over set nodes")

        #print(event_list)
        #print("output", output_node)
        for ev in event_list:
            val = df.loc[i, ev]
            #print("\t", ev, int(val))
            ie.addEvidence(ev, int(val))

            try:
                fin = round(ie.posterior(output_node)[1], 2)
            except:
                fin = "NA"
                print("network breaks at precision")
                print(file_name)
            #    fin = "NA"
            #    print("BREAKS")
                break


        #print(ie.posterior(output_node))
        name_output_list.append(output_node)

        output_list.append(val_output)
        #print("output actual",val_output)
        if fin != "NA":
            rmsd += round(abs(fin - val_output), 2)
            rms_list.append(round(abs(fin - val_output), 2))
            rounded_predicted_output.append(round(fin,0))
            if round(fin, 0) == val_output:  # we use the rounded network output -> the prediction.
                accuracy += 1
                matching_output.append(1)
            else:
                matching_output.append(0)
        else:
            fin = "NA"
            rounded_predicted_output.append("NA")

            rmsd += 1
            rms_list.append(1)
            matching_output.append("NA")


        pred_output.append(fin)

    otp = {}

    event_list = list(bn.names())  # experiment.reporters.relevant_events
    for ev in event_list:
        otp[ev] = df.loc[:,ev]



    otp["nameoutput"] = name_output_list
    otp["output"] = output_list
    otp["network_output"] = pred_output
    otp["matching"] = matching_output
    otp["RMS"] = rms_list
    otp["prediction"] = rounded_predicted_output

    otp_pd = pd.DataFrame.from_dict(otp)

    #print("accuracy", accuracy/len(df))
    #print("root mean square", rmsd/len(df))
    n = file_name.split("_", 2)
    if len(n) > 1:
        [name, dist, val] = n
    else:
        name = n[0]
        dist = "none"
        val = 0

    row = [name, dist, val, accuracy/len(df), rmsd/len(df)]
    #print(csv_name)
    #print(file_name)
    #print(path)

    with open(path+f"/stats/performance/{csv_name}_performance.csv", 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row)

    #print(file_name)


    otp_pd.to_csv(path+"/stats/runs/"+file_name+".csv", index=False)



def calculate_world_states_accuracy(file_name, path, output_node):
    network = path + "/BNs/" + file_name + ".net"
    if "param" not in file_name and "map" not in file_name:
        csv_name = file_name.split("_", 1)[0]  # we want to refer to hte original csv file
    else:
        csv_name = file_name
    csv_file = path + "/train/" + csv_name + ".csv"
    if "net" not in network:
        network = network + ".net"
    bn = gum.loadBN(network)
    df = pd.read_csv(csv_file, sep=r',',
                     skipinitialspace=True)
    ddf = df.drop_duplicates()
    event_list = list(ddf.head())  # experiment.reporters.relevant_events
    n = file_name.split("_", 2)
    if len(n) > 1:
        [name, dist, val] = n
    else:
        name = n[0]
        dist = "none"
        val = 0

    possible_states = []
    impossible_states = []

    l = list(itertools.product([1, 0], repeat=len(event_list)))
    for item in l:
        a = np.array(item)
        #print(a)
        da = pd.DataFrame(np.expand_dims(a, axis=0), columns=list(ddf.head()))
        result = pd.concat([ddf, da]).shape[0] - pd.concat([ddf, da]).drop_duplicates().shape[0]
        #print(result)
        if result == 1:
            possible_states.append(item)
        else:
            impossible_states.append(item)


    #print(l)

    output_ind = event_list.index(output_node)
    #print(output_ind)



    for state_list in [possible_states]:

        acc = 0
        rmq = 0
        bad_count = 0
        # print(network)

        list_for_rows = []
        x = ["precision", "names", "state", "posterior", "accuracy", "rmsq"]
        list_for_rows.append(x)


        if state_list == possible_states:
            state_name = "possibleStates"
        else:
            state_name = "impossibleStates"
        #print(state_name)

        print(event_list)
        for item in state_list:
            #print()
            ie = gum.LazyPropagation(bn)
            ie.addAllTargets()
            #print(item)

            #print(event_list[output_ind])
            for name in load_temporal_evidence(networks[:-4])["events"]:
                i = event_list.index(name)
                #ie.addAllTargets()
                if i != output_ind:


                    #print("\t", i, event_list[i], item[i])
                    try:
                        ie.addEvidence(event_list[i], item[i])
                        #ie.eraseTarget(event_list[i])
                        #ie.evidenceJointImpact(ie.targets(), {event_list[i]})
                        final_posterior = ie.posterior(event_list[output_ind])[1]
                        #ie.addTarget(event_list[i])
                        #ie.eraseEvidence(event_list[i])

                        #ie.addEvidence(event_list[i], item[i])
                        final_posterior = ie.posterior(event_list[output_ind])[1]
                        #print(final_posterior)

                    except:

                        final_posterior = "NA"
                        #print(f"network breaks!!  {file_name}")
                        break
            f = 0
            if final_posterior == "NA":
                #print("bad")
                acc += 0
                bad_count += 1
            else:
                #print("final posterior", final_posterior)
                #print("actual value", event_list[output_ind], item[output_ind])
                rmq += abs(int(item[output_ind]) - final_posterior)

                if int(round(final_posterior,0)) == int(item[output_ind]):
                    acc += 1
                    f = 1
                    #print("accuracy win")
                else:
                    acc += 0
                    f = 0
                    #print()
                    #print("accuracy loss")

            row = [val, event_list, item, final_posterior, f, abs(int(item[output_ind]) - final_posterior)]
            list_for_rows.append(row)
        with open(path + f"/stats/runs/{csv_name}_{state_name}_STATE_run_performance.csv", 'a', newline='') as f:
            writer = csv.writer(f)
            for row in list_for_rows:
                writer.writerow(row)

        print(file_name)
        print(f"overall accuracy {acc/len(state_list)}")
        print(f"overall rmsq {rmq/len(state_list)}")
        print(f"overall inconsistent count {bad_count/len(state_list)}")


        row = [name, val, acc/len(state_list), rmq/len(state_list), bad_count/len(state_list)]

        with open(path + f"/stats/performance/{csv_name}_{state_name}_STATE_performance.csv", 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)

        print()


    print()








def calculate_accuracy_fixed_output(file_name, path, output_node):
    '''print(network)
    print(orgDir)
    print(bnDir)
    print(os.getcwd())'''
    network = path + "/BNs/"+file_name+".net"
    if "param" not in file_name and "map" not in file_name:
        csv_name = file_name.split("_", 1)[0]  # we want to refer to hte original csv file
    else:
        csv_name = file_name
    csv_file = path + "/test/"+csv_name+".csv"

    #print(network)
    #print(csv_name)
    #print(csv_file)
    if "net" not in network:
        network = network + ".net"

    #org_dir = orgDir
    #if dir not in os.getcwd():


    bn = gum.loadBN(network)

    # todo: set evidence
    # see value of output
    # if the same +1, else +0
    # then calcualte accuracy
    # store D in some other array

    direction_dict = {}


    '''evidence = []
    for x in event_list:
        if x[0] == "E": # evidence node
            evidence.append(x)
'''


    df = pd.read_csv(csv_file, sep=r',',
            skipinitialspace = True)

    #print(df.columns)

    accuracy = 0
    rmsd = 0
    #print(output_nodes)
    network_name = []
    pred_output=[]
    matching_output=[]
    rms_list=[]
    output_list = []
    name_output_list = []
    rounded_predicted_output = []



    for i in range(0, len(df)):
        #print("NEW COMBO")
        event_list = list(bn.names())  # experiment.reporters.relevant_events
        random.shuffle(event_list)

        ie = gum.LazyPropagation(bn)
        val_output = df.loc[i, output_node]

        #print("going over set nodes")
        '''print(i)
        print(event_list)
        print("output", output_node)'''
        for ev in event_list:
            if ev != output_node:
                val = df.loc[i, ev]
                #print("\t", ev, int(val))
                ie.addEvidence(ev, int(val))
                #print(ev, val, output_node)

                try:
                    fin = round(ie.posterior(output_node)[1], 2)
                    #print(fin)
                except:
                    print("network breaks at precision")
                    print(csv_file)
                    fin = "NA"
                #    fin = "NA"
                #    print("BREAKS")
                    #print(fin)
                    break


        #print(ie.posterior(output_node))
        name_output_list.append(output_node)

        output_list.append(val_output)
        #print("output actual",val_output)
        if fin != "NA":
            rmsd += round(abs(fin - val_output), 2)
            rms_list.append(round(abs(fin - val_output), 2))
            rounded_predicted_output.append(round(fin,0))
            if round(fin, 0) == val_output:  # we use the rounded network output -> the prediction.
                accuracy += 1
                matching_output.append(1)
            else:
                matching_output.append(0)
        else:
            fin = "NA"
            rounded_predicted_output.append("NA")

            rmsd += 1
            rms_list.append(1)
            matching_output.append("NA")


        pred_output.append(fin)

    otp = {}

    event_list = list(bn.names())  # experiment.reporters.relevant_events
    for ev in event_list:
        otp[ev] = df.loc[:,ev]



    otp["nameoutput"] = name_output_list
    otp["output"] = output_list
    otp["network_output"] = pred_output
    otp["matching"] = matching_output
    otp["RMS"] = rms_list
    otp["prediction"] = rounded_predicted_output

    otp_pd = pd.DataFrame.from_dict(otp)

    #print("accuracy", accuracy/len(df))
    #print("root mean square", rmsd/len(df))
    n = file_name.split("_", 2)
    if len(n) > 1:
        [name, dist, val] = n
    else:
        name = n[0]
        dist = "none"
        val = 0

    otp_pd.to_csv(path+"/stats/fixed_output/"+file_name+"_performance_fixed_output.csv", index=False)


def load_temporal_evidence(name):
    # this should load a json dict that is written during the experiment
    d = {}
    #print(name)
    if "KB1" in name:
        d["events"] = ["jane_has_knife", "jane_and_mark_fight","jane_stabs_mark_with_knife"]
        d["values"] = [1, 1, 0]
        d["output"] = ["mark_dies"]

    elif "KB2" in name:
        d["events"] = ["jane_and_mark_fight", "jane_has_knife", "jane_threatens_mark_with_knife", "mark_hits_jane", "jane_drops_knife", "mark_falls_on_knife", "mark_dies_by_accident"]
        d["values"] = [1, 1, 1, 1, 1, 1, 0]
        d["output"] = ["mark_dies"]

    elif "KBFull" in name:
        d["events"] = ["jane_and_mark_fight", "jane_has_knife", "jane_stabs_mark_with_knife", \
        "jane_threatens_mark_with_knife", "mark_hits_jane", "jane_drops_knife", "mark_falls_on_knife", "mark_dies_by_accident"]
        d["values"] = [1, 1, 0, 1, 1, 1, 0, 0]
        d["output"] = ["mark_dies"]

    elif "StolenLaptop" in name:
        #"lost_object", "know_object", "target_object", "motive", "compromise_house",
           #                         "flees_startled", "successful_stolen", "raining", "curtains",
        if "Private" in name:
            d["events"] = ["E_object_is_gone",
                                    "E_broken_lock",
                                    "E_disturbed_house",
                                    "E_s_spotted_by_house",
                                    "E_s_spotted_with_goodie",
                                    ]
        else:
            d["events"] = ["E_object_is_gone",
                           "E_broken_lock",
                           "E_disturbed_house",
                           "E_s_spotted_by_house",
                           "E_s_spotted_with_goodie",
                           "E_private"]

        d["values"] = [1, 1, 1, 1, 1, 0]
        d["output"] = ["successful_stolen"]

    elif "GroteMarkt" in name:

        if "Private" in name:
            d["events"] = [
                "E_psych_report_1_0",
                "E_camera_1",
                "E_camera_seen_stealing_1_0",
                "E_object_gone_0"
            ]
            d["values"] = [
                1,
                1,
                1,
                1
                ]
            d["output"] = ["stealing_1_0", "object_dropped_accidentally_0"]

        else:
            d["events"] = [
                "E_valuable_1_0",
                "E_vulnerable_1_0",
                "E_psych_report_1_0",
                "E_camera_1",
                "E_sneak_1_0",
                "E_camera_seen_stealing_1_0",
                "E_object_gone_0"]
            d["values"] = [
                1,
                1,
                1,
                1,
                1,
                1,
                1]
            d["output"] = ["stealing_1_0", "object_dropped_accidentally_0"]

    elif "WalkThrough" in name:
        d["events"] = [
            "E_neighbor",
            "E_prints",
            "E_stab_wounds",
            "E_forensic"
        ]
        d["values"] = [
            1,
            1,
            1,
            1,
            ]
        d["output"] = ["mark_dies"]

    else:
        print("temporal evidence not implemented yet ")
        exit()

    return d


def get_cpts(name, path):   # we only use this for GroteMarktMaps checking cpts out
    network_name = path + "/BNs/" + name + ".net"
    bn = gum.loadBN(network_name)
    #ie = gum.LazyPropagation(bn)
    print(name, "P(seen) = 1:  ", bn.cpt("seen_1_0")[1])



def progress(name, path, temporal_evidence, params):
    x = []
    y = []
    posterior_name = []
    param_num = []
    param_name = []

    network_name = path + "/BNs/" + name+".net"
    bn = gum.loadBN(network_name)
    ie = gum.LazyPropagation(bn)


    event = temporal_evidence["events"]
    val = temporal_evidence["values"]
    output = temporal_evidence["output"][0]
    x.append("No evidence")
    y.append(round(ie.posterior(output)[1], 2))
    posterior_name.append(output)
    param_num.append(params[0])
    param_name.append(params[1])

    i = 0
    for i in range(0, len(event)):
        ie.addEvidence(event[i], val[i])
        x.append(str((event[i], val[i])))
        posterior_name.append(output)
        param_num.append(params[0])
        param_name.append(params[1])

        try:
            y.append(round(ie.posterior(output)[1], 2))
        except Exception:
            y.append("NA")

    otp = {}
    otp["evidence"] = x
    otp["posterior"] = y
    otp["posterior_name"] = posterior_name
    otp["param_num"] = param_num
    otp["param_name"] = param_name
    otp_pd = pd.DataFrame.from_dict(otp)
    otp_pd.to_csv(path + "/progress/" + name + ".csv", index=False)

def plot_posterior(path, base_network):
    folder = path+"/progress/"
    list_files = os.listdir(folder)
    list_files.sort()
    relevant_files = []

    colors = ["#fde725", "#b5de2b", "#6ece58",
              "#35b779", "#1f9e89", "#26828e",
              "#31688e", "#3e4989", "#433e85",
              "#482173", "#440154"]
    for f in list_files:
        if base_network in f:
            relevant_files.append(f)

    ax = plt.gca()
    for i in range(0, len(relevant_files)):
        file = relevant_files[i]
        param = file.split("_", 2)
        if len(param) > 2:
            [base, dis, num] = param
            num = num[:-4]
        else:
            base = file
            num = "no"

        df = pd.read_csv(folder+file, sep=r',',
            skipinitialspace=True)
        df.rename(columns={"posterior": str(num)},inplace=True)
        col = list(df.columns)
        df.plot(kind='line', x=col[0], y=col[1], color=colors[i], legend=num, title=base,  ax=ax)
        plt.xticks(range(0,len(df["evidence"])), df["evidence"], rotation='vertical')
        # Tweak spacing to prevent clipping of tick-labels
        plt.subplots_adjust(right=0.8, bottom=0.5)
        ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        plt.xlabel("Evidence added")
        plt.ylabel("Posterior of " + df["posterior_name"][0])
        plt.title("The effect of evidence on the posterior")
    file_name = path + "/plots/posterior_" + base_network + ".pdf"
    plt.savefig(file_name)
    plt.close()

def plot_posterior_base_network_only(path, base_network):
    folder = path + "/progress/"
    list_files = os.listdir(folder)
    list_files.sort()
    relevant_files = []
    flag = 0

    colors = ["#fde725", "#b5de2b", "#6ece58", "#35b779", "#1f9e89", "#26828e", "#31688e", "#3e4989", "#482878",
              "#440154"]
    for f in list_files:
        if base_network in f:
            relevant_files.append(f)

    ax = plt.gca()
    for i in range(0, len(relevant_files)):
        file = relevant_files[i]
        param = file.split("_", 2)
        if len(param) > 2:
            [base, dis, num] = param
            num = num[:-4]
            flag = 0
        else:
            base = file
            num = "no"
            flag = 1

        if flag == 1:

            df = pd.read_csv(folder + file, sep=r',',
                             skipinitialspace=True)
            df.rename(columns={"posterior": str(num)}, inplace=True)
            col = list(df.columns)
            df.plot(kind='line', x=col[0], y=col[1], color=colors[i], legend=num, title=base, ax=ax)
            plt.xticks(range(0, len(df["evidence"])), df["evidence"], rotation='vertical')
            # Tweak spacing to prevent clipping of tick-labels
            plt.subplots_adjust(right=0.8, bottom=0.5)
            ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
            plt.xlabel("Evidence added")
            plt.ylabel("Posterior of " + df["posterior_name"][0])
            plt.title("The effect of evidence on the posterior")
        file_name = path + "/plots/posterior_base_network" + base_network + ".pdf"
    plt.savefig(file_name)
    plt.close()

    #plt.show()

def plot_performance(path, base_network):
    fig, axs = plt.subplots(2, sharex='col')
    df = pd.read_csv(path+f"/stats/performance/{base_network}_possibleStates_STATE_performance.csv", sep=r',',
                     skipinitialspace=True)
    col = list(df.columns)
    df.plot(kind='line', x=col[1], y={col[2], col[4]}, title="Accuracy",  ax=axs[0])
    df.plot(kind='line', x=col[1], y=col[3], title="RMSE",  ax=axs[1])
    #plt.xticks(range(0, len(df["evidence"])), df["evidence"], rotation='vertical')
    # Tweak spacing to prevent clipping of tick-labels
    #plt.subplots_adjust(bottom=0.60)
    axs[0].set(xlabel="Disturbance", ylabel="Accuracy")
    axs[1].set(xlabel="Disturbance", ylabel="RMSE")
    file_name = path + "/plots/performance_" + base_network + ".pdf"

    plt.subplots_adjust(right=0.7, bottom=0.2)
    axs[0].legend(bbox_to_anchor=(1.04, 1), loc="upper left")
    axs[1].legend(bbox_to_anchor=(1.04, 1), loc="upper left")

    plt.savefig(file_name)
    #plt.show()
    plt.close()

def plot_performance_fixed_output(path, base_network, temporal_evidence):
    folder = path + "/stats/fixed_output/"
    list_files = os.listdir(folder)
    list_files.sort()
    fig, axs = plt.subplots(2, sharex='col')
    colors = ["#fde725", "#b5de2b", "#6ece58", "#35b779", "#1f9e89", "#26828e", "#31688e", "#3e4989", "#482878", "#440154"]
    df_list = []
    df = pd.read_csv(path + f"/stats/fixed_output/{base_network}_performance_fixed_output.csv", sep=r',',
                     skipinitialspace=True)

    df['conc'] = ""

    for event in temporal_evidence["events"]:
        df['conc'] += df[event].map(str)

    t = df.groupby('conc', as_index=False).agg({'RMS': 'mean', 'matching': 'mean'})
    t.rename(columns={'conc':'conc','RMS': f'RMS No', 'matching': 'Acc No'}, inplace=True)
    #print("first t")
    #print(t)

    c = colors.pop()
    t.plot(kind='bar', x='conc', y=f'Acc No', stacked=True, legend="No", color=c, title="Accuracy", ax=axs[0])
    t.plot(kind='bar', x='conc', y=f'RMS No', stacked=True, legend="No", color=c, title="RMS", ax=axs[1])

    df_list.append(t)
    relevant_files = []
    for f in list_files:
        #print(f)
        if base_network in f and "fixed_output" in f and "arbit" in f:
            if str(0.33) not in f and str(0.5) not in f and str(0.4) not in f and str(0.45) not in f:    # i only care about the errors in the good plots
                relevant_files.append(f)

    #print(relevant_files)
    for i in range(0, len(relevant_files)):
        file = relevant_files[i]
        param = file.split("_", 3)
        #print("param", param)
        if len(param) > 2:
            [base, dis, num, r] = param

        else:
            base = file
            num = "no"

        #print(base, dis, num)
        #for num in [ 0.05, 0.125, 0.1, 0.2, 0.25, 0.33, 0.5]:
        df = pd.read_csv(path+f"/stats/fixed_output/{base_network}_arbit_{num}_performance_fixed_output.csv", sep=r',',
                         skipinitialspace=True)

        df['conc'] = ""
        #print(num)
        for event in temporal_evidence["events"]:
            df['conc'] += df[event].map(str)

        #print(df['conc'])

        t = df.groupby('conc', as_index=False).agg({'RMS':'mean','matching':'mean'})

        t.rename(columns = {'conc':'conc', 'RMS': f'RMS {str(num)}', 'matching': f'Acc {str(num)}'},inplace=True)
        #print(list(t))
        c = colors.pop()

        t.plot(kind='bar', x='conc',y= f'Acc {str(num)}', stacked=True, legend=num, color=c, title="Accuracy",  ax=axs[0])
        t.plot(kind='bar', x='conc',y= f'RMS {str(num)}', stacked=True, legend=num, color=c, title="RMS",  ax=axs[1])
        print(t)

    plt.subplots_adjust(right=0.7, bottom = 0.2)
    axs[0].legend(bbox_to_anchor=(1.04,1), loc="upper left")
    axs[1].legend(bbox_to_anchor=(1.04,1), loc="upper left")

    file_name = path + "/plots/performance_fixed_output_" + base_network + ".pdf"
    print(file_name)
    plt.savefig(file_name)
    #plt.show()
    plt.close()


def progress_evidence(path, network_name, temporal_evidence):
    bn = gum.loadBN(path + "/BNs/" + network_name+".net")
    ie = gum.LazyPropagation(bn)



    x = []
    y_0 = []
    y_1 = []

    posterior_name = []

    #print(temporal_evidence)

    event = temporal_evidence["events"]
    val = temporal_evidence["values"]
    output_0 = temporal_evidence["output"][0]
    output_1 = temporal_evidence["output"][1]

    df = pd.read_csv(path + "/test/" + network_name + ".csv")

    #print(event)
    #print(list(df.columns))
    #print(event == list(df.columns))


    init_df_len = df.shape[0]
    df_s = df.query(f"{output_0} == {1}")
    df_a = df.query(f"{output_1} == {1}")
    df_r = df.query(f"{output_0} == {0} & {output_1} == {0}")
    #print(df.shape[0])
    if df.shape[0] > 0:
        print(df_s.shape[0] / df.shape[0], df_a.shape[0] / df.shape[0], df_r.shape[0] / df.shape[0], df.shape[0])
    else:
        print("state does not occur")

    x.append("No evidence")
    y_0.append(round(ie.posterior(output_0)[1], 2))
    y_1.append(round(ie.posterior(output_1)[1], 2))

    d_0 = []
    d_1 = []
    count = []

    if df.shape[0] > 0:
        d_0.append(round(df_s.shape[0] / df.shape[0], 2))
        d_1.append(round(df_a.shape[0] / df.shape[0], 2))
        count.append(df.shape[0])
    else:
        d_0.append(0)
        d_1.append(0)
        count.append(0)
        #print("state does not occur")


    posterior_name.append(output_0)

    i = 0
    for i in range(0, len(event)):
        print(i, event[i], val[i])
        df = df.query(f"{event[i]} == {val[i]}")
        df_s = df_s.query(f"{event[i]} == {val[i]}")
        df_a = df_a.query(f"{event[i]} == {val[i]}")
        df_r = df_r.query(f"{event[i]} == {val[i]}")

        print(df.shape)

        if df.shape[0] > 0:
            d_0.append(round(df_s.shape[0] / df.shape[0], 2))
            d_1.append(round(df_a.shape[0] / df.shape[0], 2))
            count.append(df.shape[0])

        else:
            d_0.append(0)
            d_1.append(0)
            count.append(0)

        #if df.shape[0] > 0:
        #    print(df_s.shape[0]/df.shape[0], df_a.shape[0]/df.shape[0],df_r.shape[0]/df.shape[0], df.shape[0] )
        #else:
        #    print("state does not occur")
        ie.addEvidence(event[i], val[i])
        x.append(str((event[i], val[i])))
        posterior_name.append(output_0)


        try:
            y_0.append(round(ie.posterior(output_0)[1], 2))
        except Exception:
            y_0.append(-1)

        try:
            y_1.append(round(ie.posterior(output_1)[1], 2))
        except Exception:
            y_1.append(-1)

            #y_1.append("NA")

    #print(y_0[-1], d_0[-1])
    #print(y_1[-1], d_1[-1])

    otp = {}
    otp["evidence"] = x
    otp["stealing_1_0"] = y_0
    otp["accidental_drop"] = y_1
    otp["freq_stealing_1_0"] = d_0
    otp["freq_accidental_drop"] = d_1
    otp["acc_0"] = abs(y_0[-1] - d_0[-1])
    otp["acc_1"] = abs(y_1[-1] - d_1[-1])
    otp["count"] = count[-1]/init_df_len

    #print(y_0)
    #print(y_1)

    otp["posterior_name"] = posterior_name
    otp_pd = pd.DataFrame.from_dict(otp)
    return otp_pd


def plot_evidence_posterior_base_network_only(path, base_network, temporal_evidence, it):
    df = progress_evidence(path, base_network, temporal_evidence)

    flag = 0

    colors = ["#2037ba", "#b62a2a"]
    color_id = 0
    if it < 5:
        color_id = 0
    else:
        pass
        #color_id = 1
    file = base_network
    param = file.split("_", 2)
    ax = plt.gca()

    if len(param) > 2:
        [base, dis, num] = param
        num = num[:-4]
        flag = 0
    else:
        base = file
        num = "network"
        flag = 1
    if flag == 1:
        df.rename(columns={"posterior": str(num)}, inplace=True)
        col = list(df.columns)
        #print(col)
        df.plot(kind='line', x=col[0], y=col[1], color=colors[0], legend=True, title=base, ax=ax)
        df.plot(kind='line', x=col[0], y=col[3], color=colors[0], legend=True, title=base, ax=ax, style="--")

        df.plot(kind='line', x=col[0], y=col[2], color=colors[1], legend=True, title=base, ax=ax)
        df.plot(kind='line', x=col[0], y=col[4], color=colors[1], legend=True, title=base, ax=ax, style="--")

        plt.xticks(range(0, len(df["evidence"])), df["evidence"], rotation='vertical')
        # Tweak spacing to prevent clipping of tick-labels
        plt.subplots_adjust(right=0.8, bottom=0.5)
        #ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left")
        plt.xlabel("Evidence added")
        plt.ylabel("Posterior probability")
        val = float(df["count"][0])
        #str_num = "{:.4f}".format(val*100)
        plt.title("The effect of evidence on the posterior ({val:.2f}) % of runs)".format(val=val*100))

        file_name = path + "/plots/freq/evidence_progress_" + base_network + "_{val:.4f}".format(val=val*100) + ".pdf"
        print(file_name)
        plt.savefig(file_name)
        #plt.show()
        plt.close()

    #print(df['acc_0'][0], df['acc_1'][0])

    return df['acc_0'][0], df['acc_1'][0], df["count"][0], df["evidence"]


def experiment_different_evidence(path, scn):
    #print(path)
    #print(scn)
    nw = f"{path}/BNs/{scn}.net"

    folder_path = f"{path}/plots/freq/"
    for file_object in os.listdir(folder_path):
        file_object_path = os.path.join(folder_path, file_object)
        if os.path.isfile(file_object_path) or os.path.islink(file_object_path):
            os.unlink(file_object_path)
        else:
            shutil.rmtree(file_object_path)


    d = load_temporal_evidence(nw)
    i = 1
    df = pd.read_csv(path + "/test/" + scn + ".csv")

    #print(df[d["events"]].drop_duplicates().to_dict())
    x = df[d["events"]]
    #print(df[d["events"]].drop_duplicates())
    values_list = df[d["events"]].drop_duplicates().values.tolist() # select all unique evidence states states




    a0 = []
    a1 = []
    c = []

    for l in values_list:

        d["values"] = l
        temporal_evidence = d
        ac0, ac1, count, e = plot_evidence_posterior_base_network_only(path, scn, temporal_evidence, i)
        print(e)
        print(count)
        a0.append(ac0)
        a1.append(ac1)
        c.append(count)
        i += 1

    print(a0)
    print(a1)
    print(c, sum(c))
    print("acc acc   ", round(1 - sum(a0)/len(a0), 3))
    print("acc stolen   ", round(1 - sum(a1)/len(a1), 3))








class Analysis():
    def __init__(self, scenario, output_nodes, org_dir, network_dir, train_test_split,  outcomes, test):
        # directories
        self.scenario = scenario
        self.output_nodes = output_nodes
        self.org_dir = org_dir
        self.network_dir = network_dir
        self.train_test_split = train_test_split
        self.runs = train_test_split[0]
        self.outcomes_csv = outcomes
        self.test_csv = test
        self.accuracy_csv = f"{scenario}Accuracy.csv"
        self.results = []
        self.networks = []
        self.outcome_experiment = None
        self.test_experiment = None



### intentions
#scenario = "CredibilityGame"
#scenario = "GroteMarkt"
#scenario = "StolenLaptop"
scenario = "VlekNetwork"
tr = 100
train_test_split = [tr, int(tr/10)]

runs = train_test_split[0]
test = train_test_split[1]

analysis = Analysis(scenario, [], os.getcwd(), None, train_test_split, None, None)

org_dir = os.getcwd()
csv_file_name = None

d_S = {"camera_vision":2}
d_V = {}
d_G = {"subtype":2, "map": org_dir+"/experiments/GroteMarkt/maps/groteMarkt.png"}

for (scenario, train_runs, param_dict) in [             #("StolenLaptopVision", 1000, d_S),
                                                        #("StolenLaptopPrivate", 2000, d_S),
                                                        #("StolenLaptop", 2000, d_S),
                                                        #("VlekNetwork", 500000, d_V),
                                                        ("GroteMarkt", 60, d_G),
                                                        ("GroteMarktPrivate", 60, d_G),
                                                        #("GroteMarktMaps", 1000, d_G),
                                                        #("WalkThrough", 1000, d_G)
                                        ]:

    os.chdir(org_dir)


    path = org_dir + "/experiments/" + scenario

    test_runs = int(train_runs / 100) #originally 10
    list_files = os.listdir(org_dir + "/experiments/" + scenario + "/train")
    list_files.sort()
    #print(scenario)



    experiment = Experiment(scenario=scenario, runs=train_runs, train="train",
                               param_dict=param_dict)  # we do the simple scenario
    #test_set = Experiment(scenario=scenario, runs=test_runs, train="test",
    #                      param_dict=param_dict)

    print("done with experiment")
    list_files = os.listdir(org_dir + "/experiments/" + scenario + "/train")
    list_files.sort()


    param_ar = [[0.001, 'arbit'], [0.01, 'arbit'], [0.025, 'arbit'], [0.05, 'arbit'], [0.1, 'arbit'], [0.125, 'arbit'],
                [0.2, 'arbit'], [0.25, 'arbit'], [0.33, 'arbit'],
                [0.5, 'arbit']]

    
    if ".DS_Store" in list_files:
        list_files.remove(".DS_Store")


    #print("List files", list_files)
    for train_data in list_files:
        if "pkl" in train_data:
            continue
        K2_BN_csv_only(train_data, path)

        if scenario != "StolenLaptopVision" and scenario != "GroteMarktMaps" and scenario != "WalkThrough":    # for some experiments we don't want to generate disturbances
            for (exp, params) in [
                ("arbit", param_ar)]:  # ("rounded", param_ro), ("arbit", param_ar), ("normalNoise", param_no)]:
                for p in params:
                    #print(param_ar)
                    pass
                    #disturb_cpts(path, exp, p[0], train_data[:-4])



    for train_data in list_files:
        if "pkl" in train_data:
            continue
        with open(path + f"/stats/performance/{train_data[:-4]}_performance.csv", 'w+') as f:
            f.truncate()
            writer = csv.writer(f)
            writer.writerow(["experiment", "disturbance", "value", "accuracy", "rmsq"])

        with open(path + f"/stats/performance/{train_data[:-4]}_possibleStates_STATE_performance.csv", 'w', newline='') as f:
            f.truncate()
            writer = csv.writer(f)
            writer.writerow(["experiment", "disturbance", "accuracy", "rmsq", "failed"])

        with open(path + f"/stats/performance/{train_data[:-4]}_impossibleStates_STATE_performance.csv", 'w',
                  newline='') as f:
            f.truncate()
            writer = csv.writer(f)
            writer.writerow(["experiment", "disturbance", "accuracy", "rmsq", "failed"])
        #row = [file_name, acc / len(possible_states), rmq / len(possible_states), bad_count / len(possible_states)]
            


    # now we've generated all the networks even with disturbances
    # reload the list of files and see how the disturbances affect the rest of the outputs

    disturbed_list_files = os.listdir(path + "/BNs")
    disturbed_list_files.sort()
    if ".DS_Store" in list_files:
        disturbed_list_files.remove(".DS_Store")
    disturbed_list_files = [scenario + ".net"]
    #print("disturbed files", disturbed_list_files)
    for networks in disturbed_list_files:
        if networks == ".DS_Store":
            continue

        #print(networks)
        #
        k = networks.split("_", 2)
        if len(k) > 2:
            [base, dist, num] = k
            num = num[:-4]

        else:
            dist = "none"
            num = 0


        #print("hugin")
        #hugin_converter(networks[:-4], path)

        #if scenario == "GroteMarktMaps":
        #    get_cpts(networks[:-4], path)

        print(networks[:-4])
        print("world state combinations accuracy")
        #calculate_world_states_accuracy(networks[:-4], path, load_temporal_evidence(networks[:-4])["output"][0])
        print("progress")
        experiment_different_evidence(path, networks[:-4])

        #progress(networks[:-4], path, load_temporal_evidence(networks[:-4]), [dist, num])


    ## IMAGING
    # making some nice plots of the posterior
    #print("plots")
    #for base_network in list_files:
    #    if ".DS" not in base_network and 'pkl' not in base_network:
    #        plot_performance(path, base_network[:-4])
    #        plot_posterior_base_network_only(path, base_network[:-4])
    #        plot_posterior(path, base_network[:-4])
    #        pass





exit()