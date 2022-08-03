# Collection of Database models

This repo contains a collection of "library" database models for crossreferencing various areas

# Usage
Models can be used like a library by importing models from desired subpackage in code:
```python
import budget.models as budget

wallet = budget.Wallet()
```

or by running them directly (if appropriate `__main__.py` exists):
```sh
$ python -m package
```