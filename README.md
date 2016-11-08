# election-monte-carlo.py
2016 presidential election Monte Carlo simulator based on last week's poll data using HuffPost Pollster API.

Requires Python 3, [numpy](https://github.com/numpy/numpy), [us](https://github.com/unitedstates/python-us) and [pollster](https://github.com/huffpostdata/python-pollster).

```
$ pip install numpy
$ pip install us
$ pip install pollster

$ python election-monte-carlo.py
Hillary Clinton has a 93.408% chance to win.
```

- The standard deviation of each poll is calculated using the sample size.
- The standard deviation of each state is calculated using pooled sample standard deviation.

### Reference
- [Pollster API](http://elections.huffingtonpost.com/pollster/api)
