import numpy as np
from hashlib import sha256
from typing import Optional
from tasks.schemas import State, PackedState, PackedStateSpace

class Base_state_space():

    states: list[State]
    adj_matrix: np.ndarray
    task_unique_name: str
    state_index_sequences: Optional[list[list[int]]]=None

    def initialize(self, task_unique_name):
        self.adj_matrix=np.empty(0) 
        self.states=[]
        self.task_unique_name=task_unique_name

    def pack(self, packed_state_space=None) -> PackedStateSpace:
        if packed_state_space is None:
            return PackedStateSpace(
                states = [state.pack() for state in self.states],
                adj_matrix=self.adj_matrix.tolist(),
                task_unique_name=self.task_unique_name
            )
        else:
            packed_state_space.states = [state.pack() for state in self.states]
            packed_state_space.adj_matrix = self.adj_matrix.tolist()
            return packed_state_space
    
    def unpack(self, packed_state_space: PackedStateSpace):
        self.states = [State() for i in range(0, len(packed_state_space.states))]
        [self.states[i].unpack(packed_state_space.states[i]) for i in range(0, len(packed_state_space.states))]
        self.adj_matrix = np.array(packed_state_space.adj_matrix)
        self.task_unique_name = packed_state_space.task_unique_name

    def add_traces(self, sequence_list):
        state_sequence_indices = self.infer_states(sequence_list=sequence_list, update=True)
        self.infer_state_space(state_sequence_indices)
    
    def hash_function(self, state_encoding: str):
        hashed_ast = sha256(state_encoding.encode()).hexdigest()
        return hashed_ast

    def state_encoding(self, code):
        ...

    def get_outgoing_states(self, state_index):
        outgoing_state_indices = np.where(self.adj_matrix[state_index,:] > 0)[0].tolist()
        outgoing_states = [self.states[index] for index in outgoing_state_indices]
        return outgoing_states, outgoing_state_indices

    def get_incoming_states(self, state_index):
        incoming_state_indices = self.adj_matrix[:,state_index].tolist()
        incoming_states = [self.states[index] for index in incoming_state_indices]
        return incoming_states, incoming_state_indices

    def infer_states(self, sequence_list, update=False):
        if update:
            states = [state.state for state in self.states]
            state_hashes = [self.hash_function(self.state_encoding(state.state)) for state in self.states]
        else:
            states = []
            state_hashes = []
        state_sequence_indices = []
        for i in range(0, len(sequence_list)):
            index_sequence = []
            for j, state in enumerate(sequence_list[i]):
                hashed_state = self.hash_function(self.state_encoding(state))
                if not hashed_state in state_hashes:
                    states.append(state)
                    state_hashes.append(hashed_state)
                    index_sequence.append(len(states)-1)
                else:
                    state_index = state_hashes.index(hashed_state)
                    index_sequence.append(state_index)
            state_sequence_indices.append(index_sequence)
        if len(states)==0:
            raise Exception("Zero states where inferred, not a valid state_space.")
        if update:
            self.states = self.create_states(states)
            return state_sequence_indices
        else:
            self.states = self.create_states(states)
            self.state_index_sequences = state_sequence_indices


    def create_states(self, state_list: list):
        states = [State() for i in range(0, len(state_list))]
        [state.set(state=state_list[i], hashed_state=self.state_encoding(state_list[i])) for i, state in enumerate(states)]
        return states


    def infer_state_space(self, state_index_sequences: list = None):
        """Create or expand the adjacency matrix of the state space based on a list of state sequences. 
        Assumes that self.states includes all states that occur. If not update states first with infer_states.

        Args:
            state_seqeunce_indices (list, optional): A list of state sequences (indices in a list). 
        """
        if not state_index_sequences is None:
            adj_matrix = np.zeros(shape=(len(self.states), len(self.states)))
            current_dim = self.adj_matrix.shape[0]
            adj_matrix[0:current_dim, 0:current_dim] = self.adj_matrix
        else:
            adj_matrix = np.zeros(shape=(len(self.states), len(self.states)))
            state_index_sequences = self.state_index_sequences
        for state_index_sequence in state_index_sequences:
            state_index_sequence = [index for index in state_index_sequence if not index is None]
            for i in range(0, len(state_index_sequence)-1):
                if state_index_sequence[i] is None:
                    continue
                if state_index_sequence[i+1] in state_index_sequence[:i]:
                    continue
                from_index = state_index_sequence[i]
                to_index = state_index_sequence[i+1]
                adj_matrix[from_index, to_index] += 1
            #Self-loops for final state for generelisability
            try:
                adj_matrix[to_index, to_index] += 1
            except UnboundLocalError:
                pass
        self.adj_matrix = adj_matrix

    def get_states(self):
        return self.states
    
    def prune_states(self):
        """Prune all states that are never visited.
        """
        has_incoming = np.sum(self.adj_matrix, axis=0) > 0
        has_incoming[0] = True
        self.adj_matrix = self.adj_matrix[has_incoming][:, has_incoming]
        self.states = [state for i, state in enumerate(self.states) if has_incoming[i]]

