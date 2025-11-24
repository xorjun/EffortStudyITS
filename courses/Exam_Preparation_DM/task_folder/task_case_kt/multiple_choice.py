'''
#!json!#
{
    "possible_choices": [ "Bayesian Knowledge Tracing (BKT), which estimates the probability that a student has mastered a skill based on their sequence of correct and incorrect responses.",
                        "Performance Factor Analysis (PFA), which estimates the probability that a student has mastered a skill based on their sequence of correct and incorrect responses.",  
                        "Deep Knowledge Tracing (DKT) to predict the performance of students in their tasks.",
                        "1 parameter IRT model to understand the difficulty of each item in the quizzes.",
                        "2 parameter IRT model to understand the difficulty and discrimination of each item in the quizzes."],
    "correct_choices": [true, false, false, false, true],
    "choice_explanations": ["This statement is correct. Within the BKT one can estimate the skill progress within one tailor quizz fof exercise set.", 
                            "This statement is not completely correct. PFA is most efficient for estimating the progress in several skills, while in the setting we focuse at one specific skill at each point of time.", 
                            "This statement is not correct. DKT is not optimal, if the quizzes are individual. Moreover, it does not give insights about student skills and taks efficiency. Additionally, it lacks interpretability, which is important in the sensitive educational context.",
                            "This statement is not completely correct. Only knowing the difficulty of most likely is not sufficient in the case of individualized quizzes.",
                            "This statement is correct. Difficulty and discrimination together can give better insight into suitability of an item for the individualized student tasks."]
}
#!json!#
'''

