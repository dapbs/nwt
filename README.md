nwt
=====

`nwt` is an unofficial series of use-cases of the Percolate Enterprise Content Marketing Platform API with Python and Pandas.

The Egyptian calendar is one of the [first truly scientific calendars](https://www.timecenter.com/articles/the-history-of-the-western-calendar/) according to which a year comprised of 12 months, and each month had exactly 30 days. In the ancient Egyptian religion, [Nut (Ancient Egyptian: Nwt)](https://en.wikipedia.org/wiki/Nut_(goddess)) is the goddess of the sky.


## Installation

```
pip install nwt
```


## Usage

```{python}
from nwt import PercolateClient

client = PercolateClient("USER_TOKEN")

client.get_current_user()


```

## References
* [Percolate](https://percolate.com)
* [Percolate API Documentation](https://percolate.com/docs/api/)
