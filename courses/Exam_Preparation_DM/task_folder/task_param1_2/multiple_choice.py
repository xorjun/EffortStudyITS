'''
#!json!#
{
    "possible_choices": [ "The 1-parameter IRT model only uses item discrimination rate as the parameter.",
                        "If the student ability reaches the difficulty of the task, the student will always be able to complete the task successfully.",  
                        "2-parameter IRT model requires sophisticated optimization.",
                        "The goal of the IRT is to model the chance of each student i to pass item j.",
                        "On a plot, these models intersect at the point where the student ability reaches the task difficulty."],
    "correct_choices": [false, false, true, true, true],
    "choice_explanations": ["This statement is not correct. The parameter in the 1-parameter IRT model is the difficulty of the item.", 
                            "This statement is not correct. For both models, if the ability of the student reaches the task difficulty, they have 50% chance to complete the task successfully.", 
                            "This statement is correct. 2-parameter model has a complicated formula for the item posterior, requiring optimiyzation with Bock-Aitkin approach or Markov chain Monte-Carlo.",
                            "This statement is correct. Both models in question try to model the probability of a student i to successfully complete (pass) an item j.",
                            "This statement is correct. Both models reach 1/2 pass probability for when the ability equals difficulty. In the 2-parameter model the discrimination parameter is only responsible fo the steepness of the slope."]
}
#!json!#
'''