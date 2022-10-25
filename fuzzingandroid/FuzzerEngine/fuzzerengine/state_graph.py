#!/usr/bin/python
import heapq
import math
from utils import K_Path_Traveller
from collections import Counter


class State:
    MAX_TRANSITIONS_TO_EXISTING_STATE = 5
    MAX_FITNESS = 200.0

    def __init__(self, uid):
        self.uid = uid  # Unique ID representing this state
        self.out_nodes = {}  # Direct, reachable successor states
        self.hit_count = 1  # Number of times this state was naturally reached
        self.transitions_triggered = 0  # Number of times this state was fuzzed (1 time fuzz = generate a transition to another state)
        self.restore_count = 0  # number of time this state was chosen to be restored in VirtualBox
        self.number_events_to_transition = []  # number of events which trigger a transition to another state
        self.controllable_widgets = 0  # Number of controllable widgets
        self.fitness_score = 100.0  # Used for selection (start at 100)
        self.num_transitions_to_existing_state = 0  # How many times the state was fuzzed and transitioned to an existing state
        self.penalty = 0.1
        self.reward = 0.1

        # True if a snapshot is taken for the state
        self.solid = False

    def add_child(self, child_node):
        self.out_nodes[child_node.uid] = child_node

    def add_hit_count(self):
        self.hit_count = self.hit_count + 1

    def add_restore_count(self):
        self.restore_count = self.restore_count + 1

    def add_transitions_triggered(self):
        self.transitions_triggered = self.transitions_triggered + 1

    def set_controllable_widgets(self, nr_widgets):
        self.controllable_widgets = nr_widgets

    def add_transition_to_existing_state(self):
        self.num_transitions_to_existing_state = self.num_transitions_to_existing_state + 1
        # if self.num_transitions_to_existing_state > self.MAX_TRANSITIONS_TO_EXISTING_STATE:
        self.penalize_state()

    def add_transition_to_high_coverage(self, child):
        self.reward_state()

        print "reward its child " + str(child.uid)
        child.reward_state()

    def add_transition_to_low_coverage(self, child):
        self.penalize_state()

        print "set fitness of its child "+str(child.uid)+" to 0\n"
        child.fitness_score = 0

    def penalize_state(self):
        print "===================> PENALIZE FOR STATE:"+str(self.uid)+" <====================="
        print "origin fitness_score:"+str(self.fitness_score)

        self.num_transitions_to_existing_state = 0
        self.fitness_score = self.fitness_score - (self.fitness_score * self.penalty)
        if self.fitness_score < 0:
            self.fitness_score = 0

        # self.penalty = self.penalty + 0.2
        # self.reward = 0.1

        if self.penalty > 1.00:
            self.penalty = 1.00
        print "current fitness_score:" + str(self.fitness_score)

    def reward_state(self):
        print "===================> REWARD FOR STATE:"+str(self.uid)+" <====================="
        print "origin fitness_score:"+str(self.fitness_score)
        if self.fitness_score == 0:
            self.fitness_score = 20 + self.controllable_widgets
        else:
            self.fitness_score = self.fitness_score + (self.fitness_score * self.reward)

        if self.fitness_score > State.MAX_FITNESS:
            self.fitness_score = State.MAX_FITNESS

        # self.penalty = 0.1
        # self.reward = self.reward + self.reward
        if self.reward > 1.00:
            self.reward = 1.00
        print "current fitness_score:" + str(self.fitness_score)

    def __str__(self):
        formatted_output = 'key: ' + str(self.uid)
        formatted_output = formatted_output + ' snapshot: ' + str(self.solid)
        formatted_output = formatted_output + ' hit: ' + str(self.hit_count)
        formatted_output = formatted_output + ' restore: ' + str(self.restore_count)
        formatted_output = formatted_output + ' trans: ' + str(self.transitions_triggered)
        # formatted_output = formatted_output + ' widgets: ' + str(self.controllable_widgets)
        formatted_output = formatted_output + ' fitness: ' + str(self.fitness_score)
        formatted_output = formatted_output + ' old trans: ' + str(self.num_transitions_to_existing_state)
        # formatted_output = formatted_output + ' num_events: '
        for n in self.number_events_to_transition:
            formatted_output = formatted_output + str(n) + ','
        formatted_output = formatted_output + '\n'

        edge = ''
        for k in self.out_nodes:
            edge = edge + '{' + k + '} '
        formatted_output = formatted_output + 'edges: ' + edge

        return formatted_output


class StateGraph:
    states = {}  # used as static variable containing all states

    def is_exist(self, uid):
        """
        identify whether the state exists in the graph
        :param uid: uid of the state to be checked
        """

        if self.retrieve(uid) is None:
            return False
        else:
            return True

    def retrieve(self, uid):
        """
        retrieve the state in the graph with uid
        :param uid:
        :return:
        """

        if uid in StateGraph.states:
            return StateGraph.states[uid]
        else:
            return None

    def add_node(self, state_id):
        if state_id in StateGraph.states:
            return
        new_state = State(state_id)
        StateGraph.states[state_id] = new_state

    def add_edge(self, parent_id, child_id):
        assert (parent_id != child_id), 'cannot add an edge to itself'

        parent = self.retrieve(parent_id)
        child = self.retrieve(child_id)

        assert (parent is not None), 'the parent state is not in the graph'
        assert (child is not None), 'the child state is not in the graph'

        parent.add_child(child)
        parent.add_transitions_triggered()

        child.add_hit_count()

    def dump(self):
        for key in StateGraph.states:
            print str(StateGraph.states[key])

    def get_nlargerest(self, p):
        frequent_nodes = heapq.nlargest(int(len(StateGraph.states) * p), StateGraph.states.items(),
                                        key=lambda x: x[1].hit_count)
        # print ([(x[0], x[1].transitions_triggered) for x in frequent_nodes])

        print "Frequent nodes "
        print frequent_nodes
        return frequent_nodes

    def get_least_fittest_nodes(self, p):
        frequent_nodes = heapq.nsmallest(int(math.ceil(len(StateGraph.states) * p)), StateGraph.states.items(),
                                         key=lambda x: x[1].fitness_score)

        print "Least interesting nodes: "
        print " p * num_states : " + str(math.ceil(len(StateGraph.states) * p))
        print frequent_nodes
        return frequent_nodes

    def get_nfittest(self, num_nodes):
        frequent_nodes = heapq.nlargest(num_nodes, StateGraph.states.items(), key=lambda x: x[1].fitness_score)

        print "Fittest nodes "
        print frequent_nodes
        return frequent_nodes

    def get_fittest_state(self, strategy):
        # print "Debug:" + str(strategy) + str(type(strategy))
        if strategy == 0:
            print "using fittest score ..."
            return max(filter(lambda x: x[1].solid, StateGraph.states.items()), key=lambda x: x[1].fitness_score)[1]
        if strategy == 1:
            print " using hit_count ..."
            return min(filter(lambda x: x[1].solid, StateGraph.states.items()),
                       key=lambda x: (x[1].hit_count + x[1].restore_count))[1]

    def compute_frequent_node_portion(self, nodes, top_portion):
        if len(set(nodes)) == 0:
            return 0
        return float(len([True for x in Counter([x[0] for x in self.get_nlargerest(top_portion)] + nodes).items() if
                          x[1] >= 2])) / float(len(set(nodes)))

    def get_snapshots(self):
        return filter(lambda x: x[1].solid, StateGraph.states.items())