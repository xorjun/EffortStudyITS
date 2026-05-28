from models import model_manager
from courses.schemas import Course

async def update_skill_parameters(course: Course = None, model_name: str = "default"):
    return await model_manager.get_pedagogical_model(model_name).update_course_weights(course)