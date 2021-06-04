import search
import random
import math
import utils

ids = ["204585301", "311156327"]


class MedicalProblem(search.Problem):
    """This class implements a medical problem according to problem description file"""
    _sick = 0
    _healthy = 0

    def __init__(self, initial):
        """Don't forget to implement the goal test
        You should change the initial to your own representation.
        search.Problem.__init__(self, initial) creates the root node"""
        initial1 = utils.hashabledict(initial)
        self.police = initial1['police']
        self.medics = initial1['medics']
        x = initial1['map']
        state_dict = {}
        self._rows = len(x)
        self._columns = len(x[0])
        for i in range(len(x)):
            for j in range(len(x[0])):
                state_dict[(i, j)] = (str(x[i][j]), 0)
        initial = utils.hashabledict(state_dict)
        search.Problem.__init__(self, initial)

    def actions(self, state):

        """Returns all the actions that can be executed in the given
        state. The result should be a tuple (or other iterable) of actions
        as defined in the problem description file"""
        self._healthy = 0
        self._sick = 0
        H_list = []
        S_list = []
        for i in range(self._rows):
            for j in range(self._columns):
                if state[i, j][0] == 'H':
                    self._healthy += 1
                    H_list.append(("vaccinate", (i, j)))
                elif state[i, j][0] == 'S':
                    S_list.append(("quarantine", (i, j)))
                    self._sick += 1
        # print("lists",H_list,S_list)
        if self.medics == 0 or self._healthy == 0:
            H_comb = None
        else:
            if self.medics <= self._healthy:
                H_comb = utils.combinations(H_list, self.medics)
            else:
                H_comb = utils.combinations(H_list, self._healthy)

        if self.police == 0 or self._sick == 0:
            S_comb = None
        else:
            if self.police <= self._sick:
                S_comb = utils.combinations(S_list, self.police)
            else:
                S_comb = utils.combinations(S_list,self._sick)

        H_S_list = []
        if H_comb is not None and S_comb is not None:
            for i in H_comb:
                for j in S_comb:
                    H_S_list.append([i, j])
        elif H_comb is None and S_comb is not None:
            for i in S_comb:
                H_S_list.append([i])
        elif S_comb is None and H_comb is not None:
            for i in H_comb:
                H_S_list.append([i])
        else:
            return [()]

        fixed_H_S_list = []
        for line in H_S_list:
            temp_list = list()
            for pair in line:
                for i in pair:
                    temp_list.append(i)
            fixed_H_S_list.append(tuple(temp_list))
        #print(state)
        #print(fixed_H_S_list)
        #print("end")
        # print("fixed",len(fixed_H_S_list))
        # print("state",state)
        #if self._sick == 0 or self._healthy == 0:
        #print(fixed_H_S_list,self.police,self._sick,self.medics,self._healthy)
        # print("return")
        return tuple(fixed_H_S_list)

    def result(self, state, action):
        #print("before",state)
        list_S = list()
        list_Q = list()
        list_H = list()
        new_dict = {}
        list_Q_new = list()
        for key, value in state.items():
            new_dict[key] = value
            if str(value[0]) == 'H':
                list_H = list_H + [key]
            if str(value[0]) == 'S':
                list_S = list_S + [key]
            if str(value[0]) == 'Q':
                list_Q = list_Q + [key]
        if action == 'None':
            for j in list(list_S):
                temp = int(new_dict[j][1])
                if int(temp + 1) >= 3:
                    new_dict[j] = ('H', 0)
                    list_H.append(j)
                    list_S.remove(j)
                else:
                    new_dict[j] = ('S', int(temp + 1))
            for p in list_Q:
                temp = int(new_dict[p][1])
                if int(temp + 1) >= 2:
                    new_dict[p] = ('H', 0)
                    list_H.append(p)
                    list_Q.remove(p)
                else:
                    new_dict[p] = ('Q', int(temp + 1))
            return utils.hashabledict(new_dict)
        for i in range(len(action)):
            w = action[i][1]
            if str(action[i][0]) == 'vaccinate':
                new_dict[w] = ('I', 0)
                list_H.remove(w)
            if action[i][0] == 'quarantine':
                new_dict[w] = ('Q', 0)
                list_Q_new = list_Q_new + [w]
                list_S.remove(w)
                list_Q.append(w)
        list1 = list()
        for i in list_S:
            if int(i[0] + 1) < self._rows and (int(i[0] + 1), i[1]) in list_H:
                list1 = list1 + [(int(i[0] + 1), i[1])]
            if int(i[0]) != 0 and (int(i[0] - 1), i[1]) in list_H:
                list1 = list1 + [(int(i[0] - 1), i[1])]
            if int(i[1] + 1) < self._columns and (i[0], int(i[1] + 1)) in list_H:
                list1 = list1 + [(i[0], int(i[1] + 1))]
            if int(i[1]) != 0 and (i[0], int(i[1] - 1)) in list_H:
                list1 = list1 + [(i[0], int(i[1] - 1))]
        for a in list1:
            new_dict[a] = ('S', 0)
            if a in list_H:
                list_H.remove(a)
                list_S.append(a)
        for j in list(list_S):
            if j not in list1:
                temp = int(new_dict[j][1])
                if int(temp + 1) >= 3:
                    new_dict[j] = ('H', 0)
                    list_H.append(j)
                    list_S.remove(j)
                else:
                    new_dict[j] = ('S', int(temp + 1))
        for p in list(list_Q):
            if p not in list_Q_new:
                temp = int(new_dict[p][1])
                if int(temp + 1) >= 2:
                    new_dict[p] = ('H', 0)
                    list_H.append(p)
                    list_Q.remove(p)
                else:
                    new_dict[p] = ('Q', int(temp + 1))
        #print("after",new_dict)
        return utils.hashabledict(new_dict)

    def goal_test(self, state):
        """ Given a state, checks if this is the goal state.
         Returns True if it is, False otherwise."""
        for k in range(self._rows):
            for t in range(self._columns):
                if state[k, t][0] == 'S':
                    return False
        return True


    def h(self, node):
        """ This is the heuristic. It gets a node (not a state,
        state can be accessed via node.state)
        and returns a goal distance estimate"""
        sick = 0
        count_0 = 0
        count_1 = 0
        count_2 = 0
        count_H_0 = 0
        count_H_1 = 0
        count_H_2 = 0
        will_be_sick = 0
        #healthy_nbrs_0 = 0
        #healthy_nbrs_1 = 0
        #healthy_nbrs_2 = 0

        #print(node.state,self._sick,self._healthy)

        for k in range(self._rows):
            for t in range(self._columns):
                if node.state[k, t][0] == 'S':
                    sick += 1
                    flag = 0
                    if node.state[k, t][1] == 0:
                        count_0 += 1
                        flag = 1
                    if node.state[k, t][1] == 1:
                        count_1 += 1
                        flag = 2
                    if node.state[k, t][1] == 2:
                        count_2 += 1
                        flag = 3
                    if k+1 < self._rows and node.state[k+1, t][0] == 'H':
                        if flag == 1:
                            count_H_0 += 1
                            #healthy_nbrs_0 += count_helthy_nbrs(self._rows, self._columns, node.state, k + 1, t)
                        elif flag == 2:
                            count_H_1 += 1
                            #healthy_nbrs_1 += count_helthy_nbrs(self._rows, self._columns, node.state, k + 1, t)
                        else:
                            count_H_2 += 1
                            #healthy_nbrs_2 += count_helthy_nbrs(self._rows, self._columns, node.state, k + 1, t)

                        will_be_sick += 1
                    if k != 0 and node.state[k-1, t][0] == 'H':
                        if flag == 1:
                            count_H_0 += 1
                            #healthy_nbrs_0 += count_helthy_nbrs(self._rows, self._columns, node.state, k - 1, t)
                        elif flag == 2:
                            count_H_1 += 1
                            #healthy_nbrs_1 += count_helthy_nbrs(self._rows, self._columns, node.state, k - 1, t)
                        else:
                            count_H_2 += 1
                            #healthy_nbrs_2 += count_helthy_nbrs(self._rows, self._columns, node.state, k - 1, t)
                        will_be_sick += 1

                    if t+1 < self._columns and node.state[k, t+1][0] == 'H':
                        if flag == 1:
                            count_H_0 += 1
                            #healthy_nbrs_0 += count_helthy_nbrs(self._rows, self._columns, node.state, k , t+1)
                        elif flag == 2:
                            count_H_1 += 1
                            #healthy_nbrs_1 += count_helthy_nbrs(self._rows, self._columns, node.state, k , t+1)
                        else:
                            count_H_2 += 1
                            #healthy_nbrs_2 += count_helthy_nbrs(self._rows, self._columns, node.state, k , t+1)
                        will_be_sick += 1

                    if t != 0 and node.state[k, t-1][0] == 'H':
                        if flag == 1:
                            count_H_0 += 1
                            #healthy_nbrs_0 += count_helthy_nbrs(self._rows, self._columns, node.state, k, t-1)
                        elif flag == 2:
                            count_H_1 += 1
                            #healthy_nbrs_1 += count_helthy_nbrs(self._rows, self._columns, node.state, k, t-1)
                        else:
                            count_H_2 += 1
                            #healthy_nbrs_2 += count_helthy_nbrs(self._rows, self._columns, node.state, k, t-1)
                        will_be_sick += 1
        bonus=0
        if sick <= self.police:
            return 0
        else:
            return count_0*6+count_1*2+count_2 + count_H_0*6+count_H_1*2+count_H_2 + will_be_sick*6
        #return 0

    #@staticmethod
    #def print_state(state):
    #    pass
    """Feel free to add your own functions
    (-2, -2, None) means there was a timeout"""

def count_helthy_nbrs(rows,columns,state,k,t):
    Healthy_nbrs = 0
    if k+1 < rows:
        if state[k + 1, t][0] == 'H':
            Healthy_nbrs += 1
    if k-1 >= 0:
        if state[k - 1, t][0] == 'H':
            Healthy_nbrs += 1
    if t+1 > columns:
        if state[k, t+1][0] == 'H':
            Healthy_nbrs += 1
    if t-1 >= 0:
        if state[k, t-1][0] == 'H':
            Healthy_nbrs += 1
    return Healthy_nbrs

def powerset(iterable,r):
    """powerset([1,2,3]) --> (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"""
    s = list(iterable)
    return list(utils.chain.from_iterable(utils.combinations(s, i) for i in (number+1 for number in range(r))))


def create_medical_problem(game):
    return MedicalProblem(game)

