import sys
import os
from copy import deepcopy
from shutil import copy
from pathlib import Path
import csv
import pandas as pd

PATH_TO_FOLDER = Path('~/Documents/Technion/AI/HW1/source')


def main():
    # rename_folder()
    # copy_files()
    # run_files()
    check_validity_of_solution()
    # copy files into folders
    # todo: loop over folders and run check.py to file
    # todo: loop over folders and solutions, run checker with


def rename_folder():
    with os.scandir() as it:
        count = 0
        for entry in it:
            if entry.is_dir():
                os.rename(entry, PATH_TO_FOLDER / f"{count}_submission")
                count += 1


def copy_files():
    paths_to_files = [PATH_TO_FOLDER / 'check.py']
    # paths_to_files = [PATH_TO_FOLDER / ('check_' + str(i) + '.py') for i in range(1, 20)]
    print('here')
    with os.scandir() as it:
        for entry in it:
            if entry.is_dir():
                for a_path in paths_to_files:
                    print(f'path: {a_path}, entry: {entry}')
                    copy(a_path, entry)


# def run_files():
#     with os.scandir() as it:
#         for entry in it:
#             if entry.is_dir():
#                 path_to_check = PATH_TO_FOLDER / entry / 'check.py'
#                 print(path_to_check)
#                 # exec(path_to_check.read_text())


def check_validity_of_solution():
    # path_to_file = PATH_TO_FOLDER / 'results.csv'
    data = pd.DataFrame(columns=['ID1', 'ID2'] + [f'input {i}' for i in range(1, 15)])
    with os.scandir() as it:
        for entry in it:
            if entry.is_dir():
                with open('raw_results.txt', 'r') as raw_file:
                    lines = raw_file.readlines()
                    if not lines:
                        continue
                    new_row = dict.fromkeys(['ID1', 'ID2'] + [f'input {i}' for i in range(1, 15)])
                    ids = eval(lines[0])
                    new_row['ID1'] = ids[0]
                    try:
                        new_row['ID2'] = ids[1]
                    except IndexError:
                        pass
                    number = 0
                    for line in lines:
                        if 'number' in line:
                            number = int(line.split()[2].split(':')[0])
                        elif 'GBFS' in line:
                            assert number
                            try:
                                solution = eval(line[6:])
                                if solution == (-2, -2, None):
                                    new_row[f'input {number}'] = 'Timeout'
                                    continue
                                # if -3 in solution[0]:
                                #     new_row[f'input {number}'] = 'Bug'
                                #     continue
                                a_checker = Checker()
                                result = a_checker.check_solution(inputs[number - 1], solution[2])
                                if 'Length' in result:
                                    length = int(result.split('Length is ')[1])
                                    new_row[f'input {number}'] = length
                                if 'False' in result:
                                    new_row[f'input {number}'] = 'Incorrect solution'
                            except SyntaxError as e:
                                new_row[f'input {number}'] = str(e)
                        else:
                            pass
                    data = data.append(new_row, ignore_index=True)
    pd.set_option('display.max_columns', 16)
    print(data)
    # data.to_csv(path_to_file)

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
        try:
            try:
                if len(action) == 0:
                    return True
                if len(action) > self.medical_teams + self.police_teams:
                    return False
            except TypeError:
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
                            return False
                        if effect.lower() not in ['vaccinate', 'quarantine']:
                            # raise
                            return False
                        count[effect.lower()] += 1
                        if count['vaccinate'] > self.medical_teams or count['quarantine'] > self.police_teams:
                            # raise
                            return False
                        if effect == 'vaccinate' and 'H' not in status:
                            # raise
                            return False
                        if effect == 'quarantine' and 'S' not in status:
                            # raise
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
                                return False
                            if effect.lower() not in ['vaccinate', 'quarantine']:
                                # raise
                                return False
                            count[effect.lower()] += 1
                            if count['vaccinate'] > self.medical_teams or count['quarantine'] > self.police_teams:
                                # raise
                                return False
                            if effect == 'vaccinate' and 'H' not in status:
                                # raise
                                return False
                            if effect == 'quarantine' and 'S' not in status:
                                # raise
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

if __name__ == '__main__':
    main()
