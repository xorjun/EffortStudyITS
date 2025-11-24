# Negative Log likelihood. 

## Poisson Distribution

The Poisson distribution models the number of events that occur in a fixed interval of time or space. 
It is characterized by a single parameter λ (lambda), which represents the average rate of events per interval. 
The probability mass function (PMF) for the Poisson distribution is given by:

$ P(X = k) = \frac{e^{-\lambda} \lambda^k}{k!} $

What would be the correct negative log-likelihood (NLL) function for the Poisson Distribution?

(a) $ \text{NLL}_{\text{A}}(\mu, \sigma) = \frac{1}{2} \sum_{i=1}^{n} \left( \frac{(x_i - \mu)^2}{2\sigma^2} + \log(\sigma^2) \right) $


(b) $ \text{NLL}_{\text{B}}(\lambda) = -\sum_{i=1}^{n} \left( x_i \log(\lambda) - \lambda - \log(x_i!) \right) $

(c) $ \text{NLL}_{\text{C}}(\lambda) = \lambda \sum_{i=1}^{n} x_i - n \log(\lambda) $

Note: Please use the pen & paper method first to try to derive the respective NLL yourself. 