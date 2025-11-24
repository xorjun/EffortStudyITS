from models.pedagogical.feedback.step_generator.state_space.base_selector import Base_next_step_selector
from models.pedagogical.feedback.step_generator.state_space.base_state_space import Base_state_space
from tasks.schemas import State
from services.text_embedding import text_embedding
import numpy as np


class Embedding_Selector(Base_next_step_selector):


    async def state_distance(self, state1: State, state2: State) -> float:
        """State distance based on standard ted on reduced ast states

        Args:
            state1 (_type_): State with hashed state.
            state2 (_type_): State with hashed state.
        """
        if not state1.has_embedding(): 
            state1.set_embedding(await text_embedding.embed_text(state1.state))
        if not state2.has_embedding():
            state2.set_embedding(await text_embedding.embed_text(state2.state))
        score = np.matmul(state1.state_embedding, state2.state_embedding.T)
        cos_similarity = score/(np.linalg.norm(state1.state_embedding)*np.linalg.norm(state2.state_embedding))
        cos_similarity = float(cos_similarity)
        return 1-cos_similarity
    
    async def select_for_node(self, state_space: Base_state_space, current_state: State, current_state_index: int):
        if current_state != state_space.get_states()[current_state_index]:
            raise Exception("State space doesn't match expected structure.")
        query_instruction = 'Given a partial solution to a programming task, retrieve the best next line-step towards the correct solution.'
        query_state = State()
        query_state.set(state=current_state.state, hashed_state=None)
        query_state.set_embedding(await text_embedding.embed_text(query_state.state, instruction=query_instruction))
        outgoing_states, outgoing_state_indices = state_space.get_outgoing_states(current_state_index)
        distances = [await self.state_distance(query_state, out_state) for out_state in outgoing_states]
        return outgoing_states[np.where(distances == np.min(distances))[0][0]].state
