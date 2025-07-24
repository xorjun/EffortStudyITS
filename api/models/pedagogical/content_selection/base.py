from users.schemas import User

class Base_task_selector():
    
    async def select(self, user: User, topic: str = None):
        raise NotImplementedError