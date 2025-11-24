# Negative Log likelihood. 

## Poisson Distribution

The Poisson distribution models the number of events that occur in a fixed interval of time or space. 
It is characterized by a single parameter λ (lambda), which represents the average rate of events per interval. 
The probability mass function (PMF) for the Poisson distribution is given by:

$ P(X = x) = \frac{e^{-\lambda} \lambda^x}{x!} $

What would be the correct negative log-likelihood (NLL) function for the Poisson Distribution?

$ \text{a)}\quad NLL_{A}(\mu, \sigma) = \frac{1}{2} \sum_{i=1}^{n} \left( \frac{(x_i - \mu)^2}{2\sigma^2} + \log(\sigma^2) \right) $


$ \text{b)}\quad NLL_{B}(\lambda) = -\sum_{i=1}^{n} \left( x_i \log(\lambda) - \lambda - \log(x_i!) \right) $

$ \text{c)}\quad NLL_{C}(\lambda) = \lambda \sum_{i=1}^{n} x_i - n \log(\lambda) $

Note: Please use the pen & paper method first to try to derive the respective NLL yourself. 