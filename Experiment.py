'''
From here we run the whole experiment,
for like 100 runs.

also define some global probabily stuff here, later
TODO

'''
from itertools import product

from Reporters import Reporters
from SimulationTest import StolenLaptop


class Experiment():

    def __init__(self):  # TODO: compromise house is strange
        self.runs = 2000  # to test
        self.reporters = Reporters()
        for i in range(0, self.runs):
            model = StolenLaptop(N_agents=2, N_houses=2, width=16, height=9, reporters=self.reporters)
            for j in range(20):
                model.step()
            if self.reporters.get_report_of_event('successful_stolen') == 0 and self.reporters.get_report_of_event(
                    'unsuccessful_stolen') == 0:
                # the agent decided to not steal, either because he didn't know there was something to steal,
                # of because the cost-benefit was not worth it.
                self.reporters.increase_counter_once("no_stealing")
           # print(self.reporters.history_dict[i])

            self.reporters.increase_run()
        self.print_frequencies()


    def generate_empty_tables(self, parents, child):
        comb = product([1, 0], repeat=len(parents)+1)
        list_of_possible_combinations = []
        for i in list(comb):
            new_str = ""
            for j in range(0, len(parents)+1):
                if j >= len(parents):
                    new_str += str(child[0:3]) + str(i[j])
                else:
                    new_str += str(parents[j][0:3]) + str(i[j])
            list_of_possible_combinations.append(new_str)
        conditional_dict = {}
        for item in list_of_possible_combinations:
            conditional_dict[item] = 0
        #print(conditional_dict)
        return conditional_dict


    def conditional_frequencies(self, parents, child):
        conditional_dict = self.generate_empty_tables(parents, child)
        relevant_dict = self.reporters.history_dict
        for i in range(0, self.runs):
            parent_index = ""
            for key in parents: # we only want to look at the values for the parents
                val_parent = relevant_dict[i][key]
                parent_index += str(key[0:3]) + str(val_parent)


            full = parent_index + str(child[0:3]) + str(relevant_dict[i][child])

            conditional_dict[full] += 1

        '''print("Conditionals for CHILD ", child)
        for key in conditional_dict.keys():
            print("\t", key, (conditional_dict[key]/self.runs) * 100)
        print()'''

        #print(conditional_dict)

    def generate_empty_tables_full(self, parents, child, var=2):
        comb = product([1, 0], repeat=len(parents))
        list_of_possible_combinations = []
        dict_ = {}
        list_of_dicts = []
        for i in list(comb):
            #print(i)
            dict_ = {}

            for j in range(0, len(parents)):
                dict_[parents[j]] = i[j]
                #print(parents[j], i[j])
            dict_[child] = tuple([0]*var)
            dict_["count"] = 0
            #print(dict_[child])
            list_of_dicts.append(dict_)
        #print(list_of_dicts)
        return list_of_dicts

    def conditional_frequencies_dict(self, parents, child, var=2):
        conditional_dict = self.generate_empty_tables_full(parents, child, var)
        relevant_dict = self.reporters.history_dict

        for i in range(0, self.runs):
            parent_index = ""
            #print(relevant_dict[i])
            for dict_ in conditional_dict:
                #print(dict_)
                correct_condition = True

                for key in dict_.keys():
                    var_name, value = key, dict_[key]
                    #print(var_name, value)

                    if var_name != child and var_name != "count":
                        #print("rel dict", relevant_dict[i][var_name], relevant_dict[i][var_name] != value)

                        if relevant_dict[i][var_name] != value: # we are in the right one if this is false for all of them
                            correct_condition = False
                            break
                #print(correct_condition)
                if correct_condition == True:
                    dict_["count"] += 1
                    #print("found the relevant condition")
                    #print(dict_)
                    if relevant_dict[i][child] == 1:
                        #print("child is true")
                        (pos, neg) = dict_[child]
                        dict_[child] = (pos + 1, neg)
                    else:
                        #print("child is false")
                        (pos, neg) = dict_[child]
                        dict_[child] = (pos, neg + 1)

        #print(conditional_dict)
        return conditional_dict

    def print_bayesian_net_probs(self):
        print()
        self.conditional_frequencies([], "seen_object")
        self.conditional_frequencies(["seen_object"], "target_object")
        self.conditional_frequencies(["seen_object", "target_object"], "compromise_house")
        self.conditional_frequencies(["seen_object", "target_object", "compromise_house"], "observed")
        self.conditional_frequencies(["seen_object", "target_object", "compromise_house", "observed"], "unsuccessful_stolen")
        self.conditional_frequencies(["seen_object", "target_object", "compromise_house", "observed"], "successful_stolen")
        self.conditional_frequencies(["seen_object", "target_object", "compromise_house", "observed"], "no_stealing")
        print()






    def print_frequencies(self):

        print("\t Nice frequencies")
        for key in self.reporters.pure_frequency_event_dict.keys():
            print(key, (self.reporters.pure_frequency_event_dict[key] / self.runs)*100, 100-(self.reporters.pure_frequency_event_dict[key] / self.runs)*100)
        print("________________________________________")
        #self.print_bayesian_net_probs() # TODO to do this automatically



if __name__ == "__main__":
    Experiment()