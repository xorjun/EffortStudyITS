from models.pedagogical.feedback.step_generator.state_space.base_state_space import Base_state_space
from tasks.schemas import State
from models.pedagogical.feedback.step_generator.utils.metrics import structural_metric
import random


class Base_next_step_selector():

    async def select(self, state_space: Base_state_space, current_snapshot: str):
        current_state, current_state_index  = await self.get_closest_node(state_space.states, current_snapshot)
        next_step = await self.select_for_node(state_space, current_state, current_state_index)
        return next_step

    async def get_closest_node(self, state_list: list[State], current_snapshot: str, get_min_dist: bool=False):
        current_state = State()
        current_state.set(state=current_snapshot, hashed_state=None)#state_space.hash_encoding(current_snapshot))
        state_distances = []
        min_distance = 10**50
        closest_state_index = None
        closest_state = None
        for i, state in enumerate(state_list):
            #Frage: Hat ted hier überhaupt signifikante Vorteile?
            #Reine Orientierung an der Struktur kann problematisch sein.
            state_distances.append(await self.state_distance(current_state, state))
            if state_distances[i] <= min_distance:
                min_distance = state_distances[i]
                closest_state_index = i
                closest_state = state
        if get_min_dist:
            return closest_state, closest_state_index, min_distance
        else:
            return closest_state, closest_state_index


    async def select_for_node(self, state_space: Base_state_space, current_state: State, current_state_index: int):
        if current_state != state_space.get_states()[current_state_index]:
            raise Exception("State space doesn't match expected structure.")
        outgoing_states, outgoing_state_indices = state_space.get_outgoing_states(current_state_index)
        return random.sample(outgoing_states, 1)[0].state


    async def state_distance(self, state1: State, state2: State) -> float:
        """State distance based on standard ted on reduced ast states

        Args:
            state1 (_type_): State with hashed state.
            state2 (_type_): State with hashed state.
        """
        return structural_metric(state1.hashed_state, state2.hashed_state)
