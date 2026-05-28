from beanie import Document
from typing import Optional, List
from pydantic import ConfigDict, Field, field_validator
from numpy import ndarray
import numpy as np
from bson import Binary
import json
import pickle


class Task(Document):
    unique_name: str
    display_name: str
    task: str
    example_solution: str
    tests: dict
    type: str
    prefix: str
    additional_files: Optional[list] = None
    arguments: Optional[dict]=None
    function_name: Optional[str]=None
    possible_choices: Optional[list]=None
    correct_choices: Optional[list]=None
    selected_choices: Optional[list]=None
    choice_explanations: Optional[list]=None


class PackedState(Document):

    state: str
    hashed_state: Optional[str] = None
    state_embedding: Optional[List[float]] = None
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

class State():

    state: str
    hashed_state: Optional[str]
    state_embedding: np.ndarray

    def set(self, state, hashed_state):

        self.state = state
        self.hashed_state = hashed_state
        self.state_embedding = np.empty(0)

    def set_embedding(self, state_embedding):
        self.state_embedding = state_embedding

    def has_embedding(self):
        if self.state_embedding.size == 0:
            return False
        return True
    
    def pack(self) -> PackedState:
        return PackedState(
            state=self.state,
            state_embedding=None if self.state_embedding.size == 0 else self.state_embedding.tolist(),
            hashed_state=self.hashed_state
        )
    
    def unpack(self, packed_state: PackedState):
        self.state = packed_state.state
        self.hashed_state = packed_state.hashed_state
        self.state_embedding = np.empty(0) if packed_state.state_embedding is None else np.array(packed_state.state_embedding) 

    
class PackedStateSpace(Document):

    states: list[PackedState]
    adj_matrix: list[list]
    task_unique_name: str

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


""" class State(Document):
    state: str
    hashed_state: Optional[str]=None
    state_embedding: Optional[np.ndarray] = Field(default=np.empty(0))
    
    def set_embedding(self, state_embedding: np.ndarray):
        self.state_embedding = state_embedding
    
    def has_embedding(self) -> bool:
        return self.state_embedding.size > 0
    
    @field_validator('state_embedding', mode='before')
    @classmethod
    def validate_state_embedding(cls, v):
        if isinstance(v, list):
            # Convert empty list to empty numpy array
            if not v:
                return np.empty(0)
            # Convert list to numpy array
            return np.array(v)
        elif isinstance(v, Binary):
            # Deserialize from Binary (pickle)
            return pickle.loads(v)
        elif isinstance(v, bytes):
            # Deserialize from bytes
            return pickle.loads(v)
        return v
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        bson_encoders={
            np.ndarray: lambda v: Binary(pickle.dumps(v))
        }
    )

class StateSpace(Document):
    states: list[State]
    adj_matrix: np.ndarray
    task_unique_name: str

    @field_validator('adj_matrix', mode='before')
    @classmethod
    def validate_adj_matrix(cls, v):
        if isinstance(v, list):
            # Convert list to numpy array
            return np.array(v)
        elif isinstance(v, Binary):
            # Deserialize from Binary (pickle)
            return pickle.loads(v)
        elif isinstance(v, bytes):
            # Deserialize from bytes
            return pickle.loads(v)
        return v
    
    @field_validator('states', mode='before')
    @classmethod
    def validate_states(cls, v):
        if not v:
            return []
        
        validated_states = []
        for state_data in v:
            if isinstance(state_data, State):
                # Already a State object
                validated_states.append(state_data)
            elif isinstance(state_data, dict):
                # Convert dict to State object
                # Handle state_embedding conversion
                if 'state_embedding' in state_data:
                    embedding_data = state_data['state_embedding']
                    if isinstance(embedding_data, list):
                        state_data['state_embedding'] = np.array(embedding_data) if embedding_data else np.empty(0)
                    elif isinstance(embedding_data, Binary):
                        state_data['state_embedding'] = pickle.loads(embedding_data)
                    elif isinstance(embedding_data, bytes):
                        state_data['state_embedding'] = pickle.loads(embedding_data)
                
                validated_states.append(State(**state_data))
        return validated_states
    
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        bson_encoders={
            np.ndarray: lambda v: Binary(pickle.dumps(v)),
            State: lambda v: {
                'state': v.state,
                'hashed_state': v.hashed_state,
                'state_embedding': Binary(pickle.dumps(v.state_embedding))
            }
        }
    ) """