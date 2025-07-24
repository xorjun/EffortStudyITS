from users.schemas import User

class Base_difficulty_estimation():
    
    async def select(self, user: User):
        raise NotImplementedError