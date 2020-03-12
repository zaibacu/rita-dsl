# RITA DSL

[![Documentation Status](https://readthedocs.org/projects/rita-dsl/badge/?version=latest)](http://rita-dsl.readthedocs.io/?badge=latest)
[![codecov](https://codecov.io/gh/zaibacu/rita-dsl/branch/master/graph/badge.svg)](https://codecov.io/gh/zaibacu/rita-dsl)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/zaibacu/rita-dsl/graphs/commit-activity)
[![PyPI version fury.io](https://badge.fury.io/py/rita-dsl.svg)](https://pypi.python.org/pypi/rita-dsl/)
[![PyPI download month](https://img.shields.io/pypi/dm/rita-dsl.svg)](https://pypi.python.org/pypi/rita-dsl/)
[![GitHub license](https://img.shields.io/github/license/zaibacu/rita-dsl.svg)](https://github.com/zaibacu/rita-dsl/blob/master/LICENSE)

This is a language, loosely based on language [Apache UIMA RUTA](https://uima.apache.org/ruta.html), focused on writing manual language rules, which compiles into [spaCy](https://github.com/explosion/spaCy) compatible patterns. These patterns can be used for doing [manual NER](https://spacy.io/api/entityruler) as well as used in other processes, like retokenizing and pure matching



## Links
- [Live Demo](https://rita-demo.herokuapp.com/)
- [Documentation](http://rita-dsl.readthedocs.io/)
- [QuickStart](https://rita-dsl.readthedocs.io/en/latest/quickstart/)

## Support

[![reddit](https://img.shields.io/reddit/subreddit-subscribers/ritaDSL?style=social)](https://www.reddit.com/r/ritaDSL/)
[![Gitter](https://badges.gitter.im/rita-dsl/community.svg)](https://gitter.im/rita-dsl/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

## Install

`pip install rita-dsl`

## Simple Rules example

```python
rules = """
cuts = {"fitted", "wide-cut"}
lengths = {"short", "long", "calf-length", "knee-length"}
fabric_types = {"soft", "airy", "crinkled"}
fabrics = {"velour", "chiffon", "knit", "woven", "stretch"}

{IN_LIST(cuts)?, IN_LIST(lengths), WORD("dress")}->MARK("DRESS_TYPE")
{IN_LIST(lengths), IN_LIST(cuts), WORD("dress")}->MARK("DRESS_TYPE")
{IN_LIST(fabric_types)?, IN_LIST(fabrics)}->MARK("DRESS_FABRIC")
"""
```

### Loading in spaCy
```python
import spacy
from rita.shortcuts import setup_spacy


nlp = spacy.load("en")
setup_spacy(nlp, rules_string=rules)
```

And using it:
```
>>> r = nlp("She was wearing a short wide-cut dress")
>>> [{"label": e.label_, "text": e.text} for e in r.ents]
[{'label': 'DRESS_TYPE', 'text': 'short wide-cut dress'}]
```

### Loading using Regex (standalone)
```
import rita

patterns = rita.compile_string(rules, use_engine="standalone")
```

And using it:
```
>>> list(patterns.execute("She was wearing a short wide-cut dress"))
[{'end': 38, 'label': 'DRESS_TYPE', 'start': 18, 'text': 'short wide-cut dress'}]
```
