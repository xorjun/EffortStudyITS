'''
#!json!#
{
    "possible_choices": ["Compared to the regular Markov Models, the Hidden Markov Models only know observable outputs, and not the actual states of the system.",  
                         "The state of the system at the time (t+1) is conditionally independent of the state at (t-1).",  
                         "HMM and Variational Autoencoders are equally efficient in their generative power.",
                         "Recurrent nets (RNNs) are deterministic and differentiable version of Markov models",
                         "MMs and HMMs can be represented by a state transition matrix."],
    "correct_choices": [true, true, false, true, false],
    "choice_explanations": ["This statement is correct. In HMM, the states of the system are hidden, hence the name.", 
                            "This statement is correct. This is the description of the markovian property.", 
                            "This statement is not completely correct.  HMMs are used for modeling sequential data, where the underlying system is assumed to be in one of a finite set of hidden states at each time step, while VAE tries to learn the distribution of latent representations of the data, which grants it generative power.",
                            "This statement is correct. RNNs are artificial NNs. operating over hidden state, that can be formalized with help of Markovian, discrete-time dynamic systems.",
                            "This statement is not correct. This is true for the MMs, but HMMs also involve emission matrix of the observable outputs."]
}
#!json!#
'''