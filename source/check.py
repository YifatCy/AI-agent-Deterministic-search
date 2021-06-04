import ex1
import search
import time
import sys
import os
from copy import deepcopy
from shutil import copy
from pathlib import Path
import csv
import pandas as pd


def timeout_exec(func, args=(), kwargs={}, timeout_duration=10, default=None):
    """This function will spawn a thread and run the given function
    using the args, kwargs and return the given default value if the
    timeout_duration is exceeded.
    """
    import threading
    class InterruptableThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            self.result = default

        def run(self):
            # remove try if you want program to abort at error
            # try:
            self.result = func(*args, **kwargs)
            # except Exception as e:
            #    self.result = (-3, -3, e)

    it = InterruptableThread()
    it.start()
    it.join(timeout_duration)
    if it.is_alive():
        return default
    else:
        return it.result


def check_problem(p, search_method, timeout):
    """ Constructs a problem using ex1.create_wumpus_problem,
    and solves it using the given search_method with the given timeout.
    Returns a tuple of (solution length, solution time, solution)"""

    """ (-2, -2, None) means there was a timeout
    (-3, -3, ERR) means there was some error ERR during search """

    t1 = time.time()
    s = timeout_exec(search_method, args=[p], timeout_duration=timeout)
    t2 = time.time()

    if isinstance(s, search.Node):
        solve = s
        solution = list(map(lambda n: n.action, solve.path()))[1:]
        return (len(solution), t2 - t1, solution)
    elif s is None:
        return (-2, -2, None)
    else:
        return s


def solve_problems(problems):
    solved = 0
    index = 1
    for problem in problems:
        try:
            p = ex1.create_medical_problem(problem)
        except Exception as e:
            print("Error creating problem: ", e)
            return None
        timeout = 60
        # best_first_graph_search(p, p.h)
        result = check_problem(p, (lambda p: search.best_first_graph_search(p, p.h)), timeout)
        print(index, "GBFS", result)
        a_checker = Checker()
        result_status = a_checker.check_solution(problem, result[2])
        if 'Length' in result_status:
            length = int(result_status.split('Length is ')[1])
            print(f'length {length}')
        if 'False' in result_status:
            print(f'Incorrect solution')
        index += 1
        # print(p.state)
        if result[2] != None:
            if result[0] != -3:
                solved = solved + 1



class Checker:
    def __init__(self):
        self.i_dim = 0
        self.j_dim = 0
        self.medical_teams = 0
        self.police_teams = 0
        self.state_sequence = []
        self.action_sequence = []
        self.state = None

    def check_solution(self, problem, solution):
        self.medical_teams = problem['medics']
        self.police_teams = problem['police']
        self.state = self.create_initial_state(problem['map'])

        for action in solution:
            self.state_sequence.append(deepcopy(self.state))
            self.action_sequence.append(action)
            if not self.is_action_legal(self.state, action):
                return 'False solution!'
            self.apply_action(self.state, action)

            self.change_state(self.state)
        for tile in self.state.values():
            if 'S' in tile:
                return 'False solution!'
        return f'Legal solution! Length is {len(solution)}'

    def create_initial_state(self, a_map):
        state = {}
        self.i_dim = len(a_map) + 2
        self.j_dim = len(a_map[0]) + 2
        for i in range(0, self.i_dim):
            for j in range(0, self.j_dim):
                if i == 0 or j == 0 or i == self.i_dim - 1 or j == self.j_dim - 1:
                    state[(i, j)] = 'U'
                elif 'S' in a_map[i - 1][j - 1]:
                    state[(i, j)] = 'S1'
                elif 'Q' in a_map[i - 1][j - 1]:
                    state[(i, j)] = 'Q1'
                else:
                    state[(i, j)] = a_map[i - 1][j - 1]
        return state

    def is_action_legal(self, state, action):
        #print("beg",state)
        #print("beg",action)
        try:
            try:
                if len(action) == 0:
                    return True
                if len(action) > self.medical_teams + self.police_teams:
                    #print("1",action)
                    #print("1",state)
                    return False
            except TypeError:
                #print("2",action)
                #print("2",state)
                return False

            count = {'vaccinate': 0, 'quarantine': 0}
            try:
                for atomic_action in action:
                    try:
                        # for people who did 1 extra tuple
                        if len(atomic_action) == 1:
                            atomic_action = atomic_action[0]
                        effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
                        try:
                            status = state[location]
                        except KeyError:
                            # raise
                            #print("3",action)
                            #print("3",state)
                            return False
                        if effect.lower() not in ['vaccinate', 'quarantine']:
                            # raise
                            #print("4",action)
                            #print("4",state)
                            return False
                        count[effect.lower()] += 1
                        if count['vaccinate'] > self.medical_teams or count['quarantine'] > self.police_teams:
                            # raise
                            #print("5",action)
                            #print("5",state)
                            return False
                        if effect == 'vaccinate' and 'H' not in status:
                            # raise
                            #print("6",action)
                            #print("6",state)
                            return False
                        if effect == 'quarantine' and 'S' not in status:
                            # raise
                            #print("7",action)
                            #print("7",state)
                            return False
                    except IndexError:
                        continue
            except TypeError as e:
                for action_types in action:
                    for atomic_action in action_types:
                        try:
                            effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
                            try:
                                status = state[location]
                            except KeyError:
                                # raise
                                #print("8",action)
                                #print("8",state)
                                return False
                            if effect.lower() not in ['vaccinate', 'quarantine']:
                                # raise
                                #print("9",action)
                                #print("9",action)
                                return False
                            count[effect.lower()] += 1
                            if count['vaccinate'] > self.medical_teams or count['quarantine'] > self.police_teams:
                                # raise
                                #print("10",action)
                                #print("10",state)
                                return False
                            if effect == 'vaccinate' and 'H' not in status:
                                # raise
                                #print("11",action)
                                #print("11",state)
                                return False
                            if effect == 'quarantine' and 'S' not in status:
                                # raise
                                #print("12",action)
                                #print("12",action)
                                return False
                        except IndexError:
                            continue
            return True
        except TypeError:
            # raise
            return False

    def apply_action(self, state, action):
        if len(action) == 0:
            return True
        try:
            for atomic_action in action:
                try:
                    effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
                    if 'v' in effect:
                        state[location] = 'I'
                    else:
                        state[location] = 'Q0'
                except IndexError:
                    continue
        except TypeError:
            for action_types in action:
                for atomic_action in action_types:
                    try:
                        effect, location = atomic_action[0], (atomic_action[1][0] + 1, atomic_action[1][1] + 1)
                        if 'v' in effect:
                            state[location] = 'I'
                        else:
                            state[location] = 'Q0'
                    except IndexError:
                        continue

    def change_state(self, state):
        new_state = deepcopy(state)
        # virus spread
        for i in range(1, self.i_dim):
            for j in range(1, self.j_dim):
                if state[(i, j)] == 'H' and ('S' in state[(i - 1, j)] or
                                             'S' in state[(i + 1, j)] or
                                             'S' in state[(i, j - 1)] or
                                             'S' in state[(i, j + 1)]):
                    new_state[(i, j)] = 'S1'

        # advancing sick counters
        for i in range(1, self.i_dim):
            for j in range(1, self.j_dim):
                if 'S' in state[(i, j)]:
                    turn = int(state[(i, j)][1])
                    if turn < 3:
                        new_state[(i, j)] = 'S' + str(turn + 1)
                    else:
                        new_state[(i, j)] = 'H'

                # advancing quarantine counters
                if 'Q' in state[(i, j)]:
                    turn = int(state[(i, j)][1])
                    if turn < 2:
                        new_state[(i, j)] = 'Q' + str(turn + 1)
                    else:
                        new_state[(i, j)] = 'H'

        self.state = new_state

def main():
    print(ex1.ids)
    """Here goes the input you want to check"""
    exam = [
        {
            "police": 1,
            "medics": 0,
            "map": (('S', 'H'), ('H', 'H'))
        }]


    inputs = [
        # 1
        {
            'police': 0,
            'medics': 1,
            "map": (
                ('H', 'H', 'H', 'H'),
                ('H', 'S', 'H', 'H'),
                ('H', 'Q', 'S', 'H'),
                ('S', 'H', 'H', 'H'),
            )
        },

        # 2

        {
            'police': 1,
            'medics': 1,
            "map": (
                ('H', 'H', 'H', 'H'),
                ('H', 'S', 'H', 'H'),
                ('H', 'Q', 'S', 'H'),
                ('S', 'H', 'H', 'H'),
            )
        },

        # 3
        {
            'police': 0,
            'medics': 1,
            "map": (
                ('S', 'I', 'H', 'H'),
                ('H', 'H', 'H', 'I'),
                ('Q', 'H', 'S', 'H'),
                ('I', 'H', 'H', 'H'),
            )
        },

        # 4

        {
            'police': 1,
            'medics': 1,
            "map": (
                ('S', 'I', 'H', 'H'),
                ('H', 'H', 'H', 'I'),
                ('Q', 'H', 'S', 'H'),
                ('I', 'H', 'H', 'H'),
            )
        },
        # 5
        {
            'police': 0,
            'medics': 1,
            "map": (
                ('H', 'S', 'S', 'U'),
                ('S', 'H', 'H', 'S'),
                ('H', 'U', 'H', 'H'),
                ('S', 'H', 'S', 'H'),
            )
        },
        # 6
        {
            'police': 1,
            'medics': 1,
            "map": (
                ('H', 'S', 'S', 'U'),
                ('S', 'H', 'H', 'S'),
                ('H', 'U', 'H', 'H'),
                ('S', 'H', 'S', 'H'),
            )
        },

        # 7
        {
            'police': 0,
            'medics': 1,
            "map": (
                ('H', 'I', 'S', 'U', 'H'),
                ('S', 'U', 'H', 'H', 'H'),
                ('H', 'H', 'I', 'S', 'H'),
                ('H', 'H', 'S', 'H', 'H'),
                ('S', 'H', 'H', 'H', 'S'),
            )
        },

        # 8
        {
            'police': 2,
            'medics': 1,
            "map": (
                ('H', 'U', 'H', 'H', 'H'),
                ('H', 'U', 'S', 'S', 'H'),
                ('H', 'S', 'S', 'S', 'H'),
                ('H', 'S', 'S', 'H', 'S'),
                ('I', 'H', 'H', 'U', 'H'),
            )
        },

        # 9
        {
            'police': 1,
            'medics': 1,
            "map": (
                ('S', 'H', 'S', 'H', 'Q'),
                ('S', 'S', 'H', 'H', 'H'),
                ('H', 'H', 'H', 'S', 'H'),
                ('I', 'U', 'I', 'U', 'Q'),
                ('S', 'U', 'H', 'H', 'H'),
            )
        },

        # 10

        {
            'police': 1,
            'medics': 1,
            "map": (
                ('Q', 'S', 'H', 'Q', 'H'),
                ('S', 'H', 'H', 'S', 'S'),
                ('U', 'H', 'Q', 'H', 'H'),
                ('H', 'S', 'U', 'U', 'H'),
                ('H', 'H', 'H', 'S', 'H'),
            )
        },
        # 11

        {
            'police': 1,
            'medics': 1,
            "map": (
                ('H', 'Q', 'I', 'H', 'H', 'H'),
                ('S', 'H', 'H', 'S', 'I', 'U'),
                ('U', 'H', 'H', 'U', 'H', 'U'),
                ('H', 'S', 'I', 'H', 'H', 'S'),
                ('S', 'H', 'H', 'H', 'H', 'H'),
                ('H', 'Q', 'H', 'S', 'H', 'I'),
            )
        },
        # 12
        {
            'police': 1,
            'medics': 1,
            "map": (
                ('H', 'S', 'I', 'H', 'H', 'H'),
                ('S', 'H', 'H', 'S', 'I', 'U'),
                ('U', 'H', 'H', 'U', 'S', 'U'),
                ('H', 'S', 'H', 'H', 'H', 'S'),
                ('H', 'H', 'H', 'H', 'H', 'H'),
                ('H', 'Q', 'H', 'S', 'H', 'I'),
            )
        },

        # 13
        {
            'police': 0,
            'medics': 2,
            "map": (
                ('H', 'S', 'I', 'H', 'H', 'H'),
                ('S', 'H', 'H', 'S', 'I', 'U'),
                ('U', 'H', 'H', 'U', 'S', 'U'),
                ('H', 'S', 'H', 'U', 'H', 'S'),
                ('S', 'H', 'S', 'H', 'H', 'H'),
                ('H', 'S', 'H', 'S', 'H', 'I'),
            )
        },

        # 14
        {
            'police': 1,
            'medics': 1,
            "map": (
                ('H', 'S', 'H', 'H', 'H', 'U', 'H', 'H'),
                ('H', 'U', 'H', 'H', 'S', 'H', 'H', 'H'),
                ('H', 'S', 'H', 'U', 'H', 'U', 'S', 'H'),
                ('H', 'H', 'H', 'H', 'S', 'H', 'H', 'H'),
                ('U', 'H', 'H', 'S', 'H', 'U', 'S', 'H'),
                ('H', 'U', 'H', 'U', 'H', 'H', 'U', 'S'),
                ('H', 'H', 'H', 'H', 'H', 'H', 'U', 'H'),
                ('S', 'H', 'H', 'U', 'H', 'S', 'H', 'H'),
            )
        },

        # # 15

        #     {
        #         'police': 3,
        #         'medics': 2,
        #         "map":(
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('S','U','H','H','H','S','H','U','H','H'),
        #             ('U','H','S','S','H','S','U','H','H','H'),
        #             ('S','H','H','S','H','U','S','S','H','H'),
        #             ('H','U','H','H','H','U','H','H','S','H'),
        #             ('H','U','S','H','H','H','U','H','S','H'),
        #             ('H','U','S','U','U','S','U','H','H','S'),
        #             ('S','H','H','H','H','H','H','U','H','H'),
        #             ('H','U','H','S','H','S','H','H','U','U'),
        #             ('H','H','H','S','H','H','H','H','H','H'),
        #             )
        #     },

        # # 16

        #     {
        #         'police': 4,
        #         'medics': 1,
        #         "map":(
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('S','U','H','H','H','S','H','U','H','H'),
        #             ('U','H','S','S','H','S','U','H','H','H'),
        #             ('S','H','H','S','H','U','S','S','H','H'),
        #             ('H','U','H','H','H','U','H','H','S','H'),
        #             ('H','U','S','H','H','H','U','H','S','H'),
        #             ('H','U','S','U','U','S','U','H','H','S'),
        #             ('S','H','H','H','H','H','H','U','H','H'),
        #             ('H','U','H','S','H','S','H','H','U','U'),
        #             ('H','H','H','S','H','H','H','H','H','H'),
        #             )
        #     },
        # # 17

        #     {
        #         'police': 1,
        #         'medics': 1,
        #         "map":(
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('H','S','H','H','H','H','H','H','S','H'),
        #             ('H','H','H','H','H','S','S','H','H','H'),
        #             ('H','U','H','H','H','H','H','H','H','H'),
        #             ('H','H','U','U','U','U','U','H','U','U'),
        #             ('H','U','H','S','S','S','H','H','H','H'),
        #             ('U','S','S','H','H','S','H','S','H','H'),
        #             ('H','H','S','H','H','S','H','S','H','S'),
        #             ('H','H','H','H','H','H','S','H','H','H'),
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('S','H','S','H','S','H','H','U','U','U'),
        #             ('H','H','H','S','H','U','H','H','H','H'),
        #             ('H','S','U','H','H','H','H','H','U','H'),
        #             ('H','S','H','H','H','H','H','U','S','H'),
        #             ('H','U','U','H','H','U','H','S','U','H'),
        #             ('H','U','U','H','H','S','S','H','H','H'),
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('H','S','H','S','H','S','H','H','H','H'),
        #             ('H','H','H','S','H','H','H','H','H','H'),
        #             ('U','U','U','H','U','U','U','U','U','U'),
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             )
        #     },

        # # 18
        #     {
        #         'police': 5,
        #         'medics': 3,
        #         "map":(
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('H','S','H','H','H','H','H','H','S','H'),
        #             ('H','H','H','H','H','S','S','H','H','H'),
        #             ('H','U','H','H','H','H','H','H','H','H'),
        #             ('H','H','U','U','U','U','U','H','U','U'),
        #             ('H','U','H','S','S','S','H','H','H','H'),
        #             ('U','S','S','H','H','S','H','S','H','H'),
        #             ('H','H','S','H','H','S','H','S','H','S'),
        #             ('H','H','H','H','H','H','S','H','H','H'),
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('S','H','S','H','S','H','H','U','U','U'),
        #             ('H','H','H','S','H','U','H','H','H','H'),
        #             ('H','S','U','H','H','H','H','H','U','H'),
        #             ('H','S','H','H','H','H','H','U','S','H'),
        #             ('H','U','U','H','H','U','H','S','U','H'),
        #             ('H','U','U','H','H','S','S','H','H','H'),
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('H','S','H','S','H','S','H','H','H','H'),
        #             ('H','H','H','S','H','H','H','H','H','H'),
        #             ('U','U','U','H','U','U','U','U','U','U'),
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             ('H','H','H','H','H','H','H','H','H','H'),
        #             )
        #     },
        # # 19

        #     {
        #         'police': 3,
        #         'medics': 3,
        #         "map":(
        #             ('H','H','H','S','H','H','H','S','H','H'),
        #             ('H','S','H','H','H','H','H','S','H','H'),
        #             ('H','H','H','S','H','H','S','S','S','H'),
        #             ('U','H','S','H','H','S','H','S','S','H'),
        #             ('H','U','S','H','H','S','H','S','H','H'),
        #             ('H','H','U','H','S','H','S','S','S','H'),
        #             ('H','H','H','U','H','H','H','H','S','H'),
        #             ('H','H','H','H','U','H','H','H','H','H'),
        #             ('H','H','H','H','H','U','H','H','S','H'),
        #             ('H','H','H','H','H','H','S','H','S','H'),
        #             ('H','H','H','H','H','U','S','H','H','S'),
        #             ('H','H','H','H','H','U','S','H','S','H'),
        #             ('H','H','H','H','H','H','U','S','S','H'),
        #             )
        #     },
    ]

    solve_problems(inputs)
    # problems_original = [
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('U', 'H', 'S', 'H',),
    #             ('H', 'U', 'H', 'S',),
    #             ('U', 'H', 'H', 'U',),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('U', 'H', 'S', 'H', 'S'),
    #             ('H', 'U', 'H', 'S', 'H'),
    #             ('U', 'H', 'H', 'U', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 2,
    #         "medics": 2,
    #         "map": (
    #             ('U', 'H', 'S', 'H', 'S'),
    #             ('H', 'U', 'H', 'S', 'H'),
    #             ('U', 'H', 'H', 'U', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 2,
    #         "medics": 1,
    #         "map": (
    #             ('U', 'H', 'S', 'H', 'S', 'H'),
    #             ('H', 'U', 'H', 'S', 'H', 'U'),
    #             ('U', 'H', 'H', 'U', 'H', 'I'),
    #             ('H', 'H', 'U', 'H', 'H', 'H'),
    #             ('H', 'U', 'S', 'H', 'Q', 'H'),
    #         )
    #     },
    #
    # ]
    # new_inputs_original = [
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('U', 'H', 'H', 'S', 'H'),
    #             ('U', 'U', 'U', 'H', 'U'),
    #             ('H', 'S', 'Q', 'H', 'S'),
    #             ('H', 'U', 'H', 'S', 'U'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'S', 'S', 'H'),
    #             ('S', 'H', 'H', 'S'),
    #             ('U', 'U', 'H', 'U'),
    #             ('H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'H', 'U', 'H', 'H'),
    #             ('S', 'H', 'U', 'H', 'H'),
    #             ('H', 'H', 'U', 'H', 'H'),
    #             ('U', 'U', 'U', 'H', 'Q'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'I', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'Q', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'H', 'U', 'H', 'H'),
    #             ('S', 'H', 'H', 'H', 'H'),
    #             ('H', 'H', 'U', 'H', 'H'),
    #             ('U', 'U', 'U', 'H', 'Q'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'I', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'Q', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'S', 'H', 'H'),
    #             ('S', 'H', 'H', 'S'),
    #             ('U', 'I', 'H', 'U'),
    #             ('H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 2,
    #         "medics": 1,
    #         "map": (
    #             ('S', 'H', 'H', 'S'),
    #             ('U', 'H', 'H', 'S'),
    #             ('U', 'U', 'H', 'U'),
    #             ('H', 'H', 'H', 'H'),
    #             ('I', 'H', 'H', 'S'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 2,
    #         "map": (
    #             ('H', 'S', 'S', 'H'),
    #             ('S', 'H', 'H', 'S'),
    #             ('U', 'U', 'H', 'U'),
    #             ('H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'S', 'S', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I'),
    #             ('U', 'U', 'H', 'U', 'Q'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'Q', 'H', 'S', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 3,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'S', 'S', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I'),
    #             ('U', 'U', 'H', 'U', 'Q'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'Q', 'H', 'S', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 2,
    #         "map": (
    #             ('H', 'S', 'S', 'H', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I', 'U'),
    #             ('U', 'U', 'H', 'U', 'Q', 'U'),
    #             ('H', 'H', 'H', 'H', 'H', 'S'),
    #             ('H', 'H', 'H', 'H', 'H', 'H'),
    #             ('H', 'Q', 'H', 'S', 'H', 'I'),
    #         )
    #     },
    #
    #     {
    #         "police": 2,
    #         "medics": 2,
    #         "map": (
    #             ('H', 'S', 'I', 'H', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I', 'U'),
    #             ('U', 'H', 'H', 'U', 'S', 'U'),
    #             ('H', 'S', 'H', 'H', 'H', 'S'),
    #             ('H', 'H', 'H', 'H', 'H', 'H'),
    #             ('H', 'Q', 'H', 'S', 'H', 'I'),
    #         )
    #     },
    #
    # ]
    # students_problems = [
    #     #1
    #     {'police': 1,
    #      'medics': 1,
    #      'map': (
    #         ('H', 'I', 'I', 'I', 'H', 'S', 'S', 'S'),
    #         ('H', 'S', 'Q', 'S', 'S', 'Q', 'H', 'H'),
    #         ('Q', 'S', 'H', 'U', 'Q', 'I', 'H', 'H'),
    #         ('U', 'S', 'H', 'H', 'H', 'H', 'S', 'I'),
    #         ('H', 'H', 'H', 'I', 'H', 'H', 'H', 'S'))},
    #     #2
    #     {'police': 1,
    #      'medics': 2,
    #      'map': (
    #         ('H', 'I', 'I', 'I', 'H', 'S', 'S', 'S'),
    #         ('H', 'S', 'Q', 'S', 'S', 'Q', 'H', 'H'),
    #         ('Q', 'S', 'H', 'U', 'Q', 'I', 'H', 'H'),
    #         ('U', 'S', 'H', 'H', 'H', 'H', 'S', 'I'),
    #         ('H', 'H', 'H', 'I', 'H', 'H', 'H', 'S'))},
    #     #3
    #     {'police': 2,
    #      'medics': 1,
    #      'map': (
    #         ('H', 'I', 'I', 'I', 'H', 'S', 'S', 'S'),
    #         ('H', 'S', 'Q', 'S', 'S', 'Q', 'H', 'H'),
    #         ('Q', 'S', 'H', 'U', 'Q', 'I', 'H', 'H'),
    #         ('U', 'S', 'H', 'H', 'H', 'H', 'S', 'I'),
    #         ('H', 'H', 'H', 'I', 'H', 'H', 'H', 'S'))},
    #     #4
    #     {'police': 1,
    #      'medics': 1,
    #      'map': (
    #         ('U', 'H', 'U', 'H', 'Q', 'H'),
    #         ('H', 'I', 'H', 'H', 'H', 'H'),
    #         ('Q', 'U', 'I', 'H', 'H', 'H'),
    #         ('H', 'H', 'H', 'H', 'H', 'H'),
    #         ('H', 'S', 'H', 'S', 'H', 'I'))},
    #     #5
    #     {'police': 1,
    #      'medics': 2,
    #      'map': (
    #         ('U', 'H', 'U', 'H', 'Q', 'H'),
    #         ('H', 'I', 'H', 'H', 'H', 'H'),
    #         ('Q', 'U', 'I', 'H', 'H', 'H'),
    #         ('H', 'H', 'H', 'H', 'H', 'H'),
    #         ('H', 'S', 'H', 'S', 'H', 'I'))},
    #     #6
    #     {'police': 2,
    #      'medics': 1,
    #      'map': (
    #         ('U', 'H', 'U', 'H', 'Q', 'H'),
    #         ('H', 'I', 'H', 'H', 'H', 'H'),
    #         ('Q', 'U', 'I', 'H', 'H', 'H'),
    #         ('H', 'H', 'H', 'H', 'H', 'H'),
    #         ('H', 'S', 'H', 'S', 'H', 'I'))},
    #     #7
    #     {'police': 2,
    #      'medics': 2,
    #      'map': (
    #         ('U', 'H', 'U', 'H', 'Q', 'H'),
    #         ('H', 'I', 'H', 'H', 'H', 'H'),
    #         ('Q', 'U', 'I', 'H', 'H', 'H'),
    #         ('H', 'H', 'H', 'H', 'H', 'H'),
    #         ('H', 'S', 'H', 'S', 'H', 'I'))},
    #     #8
    #     {'police': 1,
    #      'medics': 1,
    #      'map': (
    #         ('Q', 'I', 'H', 'S', 'I', 'H'),
    #         ('I', 'H', 'U', 'H', 'H', 'I'),
    #         ('S', 'U', 'H', 'I', 'H', 'H'),
    #         ('H', 'H', 'S', 'H', 'H', 'H'),
    #         ('S', 'H', 'H', 'U', 'H', 'S'),
    #         ('H', 'H', 'H', 'H', 'I', 'S'))},
    #     #9
    #     {'police': 1,
    #      'medics': 2,
    #      'map': (
    #         ('Q', 'I', 'H', 'S', 'I', 'H'),
    #         ('I', 'H', 'U', 'H', 'H', 'I'),
    #         ('S', 'U', 'H', 'I', 'H', 'H'),
    #         ('H', 'H', 'S', 'H', 'H', 'H'),
    #         ('S', 'H', 'H', 'U', 'H', 'S'),
    #         ('H', 'H', 'H', 'H', 'I', 'S'))},
    #     #10
    #     {'police': 2,
    #      'medics': 1,
    #      'map': (
    #         ('Q', 'I', 'H', 'S', 'I', 'H'),
    #         ('I', 'H', 'U', 'H', 'H', 'I'),
    #         ('S', 'U', 'H', 'I', 'H', 'H'),
    #         ('H', 'H', 'S', 'H', 'H', 'H'),
    #         ('S', 'H', 'H', 'U', 'H', 'S'),
    #         ('H', 'H', 'H', 'H', 'I', 'S'))},
    #     #11
    #     {'police': 2,
    #      'medics': 2,
    #      'map': (
    #         ('Q', 'I', 'H', 'S', 'I', 'H'),
    #         ('I', 'H', 'U', 'H', 'H', 'I'),
    #         ('S', 'U', 'H', 'I', 'H', 'H'),
    #         ('H', 'H', 'S', 'H', 'H', 'H'),
    #         ('S', 'H', 'H', 'U', 'H', 'S'),
    #         ('H', 'H', 'H', 'H', 'I', 'S'))},
    #     #12
    #     {'police': 1,
    #      'medics': 1,
    #      'map': (
    #         ('H', 'H', 'H', 'H', 'U', 'S', 'U', 'H'),
    #         ('H', 'I', 'H', 'Q', 'H', 'I', 'S', 'H'),
    #         ('H', 'H', 'Q', 'H', 'H', 'S', 'H', 'H'),
    #         ('H', 'H', 'Q', 'H', 'S', 'H', 'S', 'H'),
    #         ('Q', 'H', 'U', 'U', 'H', 'H', 'H', 'H'),
    #         ('U', 'H', 'U', 'S', 'S', 'H', 'Q', 'H'))},
    #     #13
    #     {'police': 1,
    #      'medics': 2,
    #      'map': (
    #         ('H', 'H', 'H', 'H', 'U', 'S', 'U', 'H'),
    #         ('H', 'I', 'H', 'Q', 'H', 'I', 'S', 'H'),
    #         ('H', 'H', 'Q', 'H', 'H', 'S', 'H', 'H'),
    #         ('H', 'H', 'Q', 'H', 'S', 'H', 'S', 'H'),
    #         ('Q', 'H', 'U', 'U', 'H', 'H', 'H', 'H'),
    #         ('U', 'H', 'U', 'S', 'S', 'H', 'Q', 'H'))},
    #     #14
    #     {'police': 2,
    #      'medics': 1,
    #      'map': (
    #         ('H', 'H', 'H', 'H', 'U', 'S', 'U', 'H'),
    #         ('H', 'I', 'H', 'Q', 'H', 'I', 'S', 'H'),
    #         ('H', 'H', 'Q', 'H', 'H', 'S', 'H', 'H'),
    #         ('H', 'H', 'Q', 'H', 'S', 'H', 'S', 'H'),
    #         ('Q', 'H', 'U', 'U', 'H', 'H', 'H', 'H'),
    #         ('U', 'H', 'U', 'S', 'S', 'H', 'Q', 'H'))},
    #     #15
    #     {'police': 1,
    #      'medics': 1,
    #      'map': (
    #         ('H', 'S', 'Q', 'H', 'H'),
    #         ('Q', 'H', 'I', 'Q', 'U'),
    #         ('H', 'H', 'S', 'H', 'H'),
    #         ('H', 'H', 'S', 'H', 'U'),
    #         ('H', 'Q', 'H', 'S', 'U'),
    #         ('H', 'Q', 'S', 'Q', 'I'),
    #         ('H', 'H', 'S', 'U', 'H'))},
    #     #16
    #     {'police': 1,
    #      'medics': 2,
    #      'map': (
    #         ('H', 'S', 'Q', 'H', 'H'),
    #         ('Q', 'H', 'I', 'Q', 'U'),
    #         ('H', 'H', 'S', 'H', 'H'),
    #         ('H', 'H', 'S', 'H', 'U'),
    #         ('H', 'Q', 'H', 'S', 'U'),
    #         ('H', 'Q', 'S', 'Q', 'I'),
    #         ('H', 'H', 'S', 'U', 'H'))},
    #     #17
    #     {'police': 2,
    #      'medics': 1,
    #      'map': (
    #         ('H', 'S', 'Q', 'H', 'H'),
    #         ('Q', 'H', 'I', 'Q', 'U'),
    #         ('H', 'H', 'S', 'H', 'H'),
    #         ('H', 'H', 'S', 'H', 'U'),
    #         ('H', 'Q', 'H', 'S', 'U'),
    #         ('H', 'Q', 'S', 'Q', 'I'),
    #         ('H', 'H', 'S', 'U', 'H'))},
    #     #18
    #     {'police': 2,
    #      'medics': 2,
    #      'map': (
    #         ('H', 'S', 'Q', 'H', 'H'),
    #         ('Q', 'H', 'I', 'Q', 'U'),
    #         ('H', 'H', 'S', 'H', 'H'),
    #         ('H', 'H', 'S', 'H', 'U'),
    #         ('H', 'Q', 'H', 'S', 'U'),
    #         ('H', 'Q', 'S', 'Q', 'I'),
    #         ('H', 'H', 'S', 'U', 'H'))},
    #     #19
    #     {'police': 2,
    #      'medics': 1,
    #      'map': (
    #         ('H', 'I', 'Q', 'H', 'H', 'H'),
    #         ('H', 'U', 'H', 'H', 'S', 'H'),
    #         ('S', 'Q', 'H', 'H', 'U', 'H'),
    #         ('H', 'H', 'H', 'H', 'H', 'H'),
    #         ('Q', 'H', 'S', 'S', 'H', 'H'),
    #         ('H', 'S', 'U', 'H', 'S', 'H'),
    #         ('S', 'I', 'I', 'S', 'H', 'S'))},
    #     #20
    #     {'police': 1,
    #      'medics': 1,
    #      'map': (
    #         ('Q', 'Q', 'S', 'I', 'H', 'H'),
    #         ('I', 'H', 'Q', 'H', 'Q', 'H'),
    #         ('H', 'S', 'H', 'Q', 'H', 'H'),
    #         ('H', 'U', 'U', 'U', 'I', 'H'),
    #         ('H', 'I', 'U', 'I', 'I', 'I'),
    #         ('S', 'Q', 'S', 'I', 'H', 'S'),
    #         ('U', 'H', 'H', 'H', 'H', 'S'),
    #         ('S', 'H', 'S', 'S', 'H', 'H'))},
    #     #21
    #     {'police': 1,
    #      'medics': 2,
    #      'map': (
    #         ('Q', 'Q', 'S', 'I', 'H', 'H'),
    #         ('I', 'H', 'Q', 'H', 'Q', 'H'),
    #         ('H', 'S', 'H', 'Q', 'H', 'H'),
    #         ('H', 'U', 'U', 'U', 'I', 'H'),
    #         ('H', 'I', 'U', 'I', 'I', 'I'),
    #         ('S', 'Q', 'S', 'I', 'H', 'S'),
    #         ('U', 'H', 'H', 'H', 'H', 'S'),
    #         ('S', 'H', 'S', 'S', 'H', 'H'))},
    #     #22
    #     {'police': 2,
    #      'medics': 1,
    #      'map': (
    #         ('Q', 'Q', 'S', 'I', 'H', 'H'),
    #         ('I', 'H', 'Q', 'H', 'Q', 'H'),
    #         ('H', 'S', 'H', 'Q', 'H', 'H'),
    #         ('H', 'U', 'U', 'U', 'I', 'H'),
    #         ('H', 'I', 'U', 'I', 'I', 'I'),
    #         ('S', 'Q', 'S', 'I', 'H', 'S'),
    #         ('U', 'H', 'H', 'H', 'H', 'S'),
    #         ('S', 'H', 'S', 'S', 'H', 'H'))},
    #     #23
    #     {'police': 1,
    #      'medics': 1,
    #      'map': (
    #         ('Q', 'U', 'I', 'H', 'S'),
    #         ('H', 'H', 'Q', 'H', 'Q'),
    #         ('Q', 'H', 'H', 'U', 'S'),
    #         ('H', 'Q', 'H', 'Q', 'S'),
    #         ('S', 'H', 'H', 'I', 'H'),
    #         ('S', 'H', 'H', 'H', 'U'),
    #         ('H', 'H', 'H', 'Q', 'Q'),
    #         ('I', 'H', 'H', 'Q', 'H'))},
    #     #24
    #     {'police': 1,
    #      'medics': 2,
    #      'map': (
    #         ('Q', 'U', 'I', 'H', 'S'),
    #         ('H', 'H', 'Q', 'H', 'Q'),
    #         ('Q', 'H', 'H', 'U', 'S'),
    #         ('H', 'Q', 'H', 'Q', 'S'),
    #         ('S', 'H', 'H', 'I', 'H'),
    #         ('S', 'H', 'H', 'H', 'U'),
    #         ('H', 'H', 'H', 'Q', 'Q'),
    #         ('I', 'H', 'H', 'Q', 'H'))},
    #     #25
    #     {'police': 2,
    #      'medics': 1,
    #      'map': (
    #         ('Q', 'U', 'I', 'H', 'S'),
    #         ('H', 'H', 'Q', 'H', 'Q'),
    #         ('Q', 'H', 'H', 'U', 'S'),
    #         ('H', 'Q', 'H', 'Q', 'S'),
    #         ('S', 'H', 'H', 'I', 'H'),
    #         ('S', 'H', 'H', 'H', 'U'),
    #         ('H', 'H', 'H', 'Q', 'Q'),
    #         ('I', 'H', 'H', 'Q', 'H'))},
    # ]
    # problems_original_one_team = [
    #     {
    #         "police": 1,
    #         "medics": 0,
    #         "map": (
    #             ('U', 'H', 'S', 'H',),
    #             ('H', 'U', 'H', 'S',),
    #             ('U', 'H', 'H', 'U',),
    #         )
    #     },
    #
    #     {
    #         "police": 0,
    #         "medics": 1,
    #         "map": (
    #             ('U', 'H', 'S', 'H', 'S'),
    #             ('H', 'U', 'H', 'S', 'H'),
    #             ('U', 'H', 'H', 'U', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 0,
    #         "medics": 2,
    #         "map": (
    #             ('U', 'H', 'S', 'H', 'S'),
    #             ('H', 'U', 'H', 'S', 'H'),
    #             ('U', 'H', 'H', 'U', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 2,
    #         "medics": 0,
    #         "map": (
    #             ('U', 'H', 'S', 'H', 'S', 'H'),
    #             ('H', 'U', 'H', 'S', 'H', 'U'),
    #             ('U', 'H', 'H', 'U', 'H', 'I'),
    #             ('H', 'H', 'U', 'H', 'H', 'H'),
    #             ('H', 'U', 'S', 'H', 'Q', 'H'),
    #         )
    #     },
    #
    # ]
    # only_sick = [
    #     {
    #     "police": 5,
    #     "medics": 5,
    #     "map": (
    #         ('S', 'S', 'S', 'S', 'S', 'S'),
    #         ('S', 'S', 'S', 'S', 'S', 'S'),
    #         ('S', 'S', 'S', 'S', 'S', 'S'),
    #         ('S', 'S', 'S', 'S', 'S', 'S'),
    #         ('S', 'S', 'S', 'S', 'S', 'S'),
    #         ('S', 'S', 'S', 'S', 'S', 'S'),
    #     )
    # }]
    #
    # check = [
    #     {
    #         "police": 2,
    #         "medics": 2,
    #         "map": (
    #             ('H', 'S', 'I', 'H', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I', 'U'),
    #             ('U', 'H', 'H', 'U', 'S', 'U'),
    #             ('H', 'S', 'H', 'H', 'H', 'S'),
    #             ('H', 'H', 'H', 'H', 'H', 'H'),
    #         )
    #     },
    #     {
    #         "police": 2,
    #         "medics": 2,
    #         "map": (
    #             ('H', 'S', 'I', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I'),
    #             ('U', 'H', 'H', 'U', 'S'),
    #             ('H', 'S', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'Q', 'H', 'S', 'H'),
    #         )
    #     },
    #     {
    #         "police": 2,
    #         "medics": 2,
    #         "map": (
    #             ('H', 'S', 'I', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I'),
    #             ('U', 'H', 'H', 'U', 'S'),
    #             ('H', 'S', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #         )
    #     },
    #     {
    #         "police": 2,
    #         "medics": 2,
    #         "map": (
    #             ('H', 'S', 'I', 'H', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I', 'U'),
    #             ('U', 'H', 'H', 'U', 'S', 'U'),
    #             ('H', 'S', 'H', 'H', 'H', 'S'),
    #             ('H', 'H', 'H', 'H', 'H', 'H'),
    #             ('H', 'Q', 'H', 'S', 'H', 'I'),
    #         )
    #     }
    # ]
    #
    # # solve_problems(check)
    #
    # print("1st Input")
    # solve_problems(problems_original)
    # print("2sd Input")
    # solve_problems(new_inputs_original)
    # print("Student Input")
    # solve_problems(students_problems)
    # print("1st Input with team change (only one type of team)")
    # solve_problems(problems_original_one_team)
    # print("Only sick Input")
    # solve_problems(only_sick)
    #
    # check2 = [
    #     {
    #         "police": 4,
    #         "medics": 1,
    #         "map": (
    #             ('S', 'S'),
    #             ('S', 'S'),
    #         )
    #     },
    # ]
    # print("No police")
    # solve_problems(check2)

    # not_reach_goal = [
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('U', 'H', 'H', 'S', 'H'),
    #             ('U', 'U', 'U', 'H', 'U'),
    #             ('H', 'S', 'Q', 'H', 'S'),
    #             ('H', 'U', 'H', 'S', 'U'),
    #         )
    #     },
    #     # {
    #     #     "police": 1,
    #     #     "medics": 1,
    #     #     "map": (
    #     #         ('H', 'S', 'H', 'H'),
    #     #         ('S', 'H', 'H', 'S'),
    #     #         ('U', 'I', 'H', 'U'),
    #     #         ('H', 'H', 'H', 'H'),
    #     #     )
    #     # },
    # ]
    # solve_problems(not_reach_goal)

    # problems = [
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('U', 'H', 'S', 'H',),
    #             ('H', 'U', 'H', 'S',),
    #             ('U', 'H', 'H', 'U',),
    #         )
    #     },
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #                     ('U', 'H', 'S', 'H', 'S'),
    #                     ('H', 'U', 'H', 'S', 'H'),
    #                     ('U', 'H', 'H', 'U', 'H'),
    #                     ('H', 'H', 'H', 'H', 'H'),
    #                 )
    #     },
    #     {
    #         "police": 2,
    #         "medics": 1,
    #         "map": (
    #             ('U', 'H', 'S', 'H', 'S', 'H'),
    #             ('H', 'U', 'H', 'S', 'H', 'U'),
    #             ('U', 'H', 'H', 'U', 'H', 'I'),
    #             ('H', 'H', 'U', 'H', 'H', 'H'),
    #             ('H', 'U', 'S', 'H', 'Q', 'H'),
    #         )
    #     },
    # ]
    # new_inputs = [
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('U', 'H', 'H', 'S', 'H'),
    #             ('U', 'U', 'U', 'H', 'U'),
    #             ('H', 'S', 'Q', 'H', 'S'),
    #             ('H', 'U', 'H', 'S', 'U'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'S', 'S', 'H'),
    #             ('S', 'H', 'H', 'S'),
    #             ('U', 'U', 'H', 'U'),
    #             ('H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'H', 'U', 'H', 'H'),
    #             ('S', 'H', 'U', 'H', 'H'),
    #             ('H', 'H', 'U', 'H', 'H'),
    #             ('U', 'U', 'U', 'H', 'Q'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'I', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'Q', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'H', 'U', 'H', 'H'),
    #             ('S', 'H', 'H', 'H', 'H'),
    #             ('H', 'H', 'U', 'H', 'H'),
    #             ('U', 'U', 'U', 'H', 'Q'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'I', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'Q', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'S', 'H', 'H'),
    #             ('S', 'H', 'H', 'S'),
    #             ('U', 'I', 'H', 'U'),
    #             ('H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 2,
    #         "medics": 1,
    #         "map": (
    #             ('S', 'H', 'H', 'S'),
    #             ('U', 'H', 'H', 'S'),
    #             ('U', 'U', 'H', 'U'),
    #             ('H', 'H', 'H', 'H'),
    #             ('I', 'H', 'H', 'S'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 2,
    #         "map": (
    #             ('H', 'S', 'S', 'H'),
    #             ('S', 'H', 'H', 'S'),
    #             ('U', 'U', 'H', 'U'),
    #             ('H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H'),
    #         )
    #     },
    #
    #     {
    #         "police": 1,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'S', 'S', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I'),
    #             ('U', 'U', 'H', 'U', 'Q'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'Q', 'H', 'S', 'H'),
    #         )
    #     },
    #     {
    #         "police": 1,
    #         "medics": 2,
    #         "map": (
    #             ('H', 'S', 'S', 'H', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I', 'U'),
    #             ('U', 'U', 'H', 'U', 'Q', 'U'),
    #             ('H', 'H', 'H', 'H', 'H', 'S'),
    #             ('H', 'H', 'H', 'H', 'H', 'H'),
    #             ('H', 'Q', 'H', 'S', 'H', 'I'),
    #         )
    #     },
    #
    #
    #
    # ]
    # permutation_problem = [
    #     {
    #         "police": 3,
    #         "medics": 1,
    #         "map": (
    #             ('H', 'S', 'S', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I'),
    #             ('U', 'U', 'H', 'U', 'Q'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #             ('H', 'Q', 'H', 'S', 'H'),
    #         )
    #     },
    # ]
    # hard_problem = [
    #     {
    #         "police": 2,
    #         "medics": 2,
    #         "map": (
    #             ('H', 'S', 'I', 'H', 'H', 'H'),
    #             ('S', 'H', 'H', 'S', 'I', 'U'),
    #             ('U', 'H', 'H', 'U', 'S', 'U'),
    #             ('H', 'S', 'H', 'H', 'H', 'S'),
    #             ('H', 'H', 'H', 'H', 'H', 'H'),
    #             ('H', 'Q', 'H', 'S', 'H', 'I'),
    #         )
    #     },
    # ]
    # action_problem = [
    #     {
    #         "police": 2,
    #         "medics": 2,
    #         "map": (
    #             ('U', 'H', 'S', 'H', 'S'),
    #             ('H', 'U', 'H', 'S', 'H'),
    #             ('U', 'H', 'H', 'U', 'H'),
    #             ('H', 'H', 'H', 'H', 'H'),
    #         )
    #     },
    # ]
    #
    # solve_problems(action_problem)
    # solve_problems(problems)
    # solve_problems(new_inputs)
    # solve_problems(permutation_problem)
    # solve_problems(hard_problem)


if __name__ == '__main__':
    main()
