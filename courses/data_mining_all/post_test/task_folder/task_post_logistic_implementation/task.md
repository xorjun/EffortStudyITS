# Performance Factory Analysis Implementation

Assume we have an array `data` that contains a sequence of zeros and ones for a student, where zeros indicate failures and ones indicate successes. Then, what does the following code do?

```python
x = np.zeros(len(data))
for t in range(len(data)-1):
    x[t+1] = x[t] + data[t]
```