'''
#!json!#
{
    "possible_choices": ["Biases can appear at each stage of user interaction with their recommendtions: from the data, behaviour of algorithm, or user responses themselves.",  
                         "Biases tend to have lesser impact over time.",  
                         "Popular choices of the majority of users are usually good recommendation candidates.",
                         "Defining a recommendation goal is a complex task in the educational context.",
                         "The nDCG is the best metric to evaluate the efficiency of recommendations."],
    "correct_choices": [true, false, false, true, false],
    "choice_explanations": ["This statement is correct. The example would be inductive bias (data), conformity bias (users), popularity bias (algorithm).", 
                            "This statement is not correct. Biases tend to amplify within the feedback loop, rendering their effects more severe over time.", 
                            "This statement is not completely correct. This is the reason behind the popularity bias, and it often leads to the discrimination of smaller user subgroups, or underrepresentation of new items.",
                            "This statement is correct. It is often challending to choose what exactly a recommender should optimize: skill growth, task completion, number of courses taken, etc.",
                            "This statement is not correct. While nDCG is indeed a very popular and useful metric, it is important to note that the evaluation metric should first of all correspond to your recommendation and optimization target."]
}
#!json!#
'''
