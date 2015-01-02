Yet Another Description Generator (YADG)
========================================

This repository contains the source code of [Yet Another Description Generator (YADG)](https://yadg.cc).

Development
-----------

The python packages that are needed to run YADG are listed in `requirements.txt`.

Additionally [rabbitmq](http://www.rabbitmq.com/) has to be installed to run Celery.

If all dependencies are met a development server can be started with:

    $ python manage.py celeryd
    $ python manage.py runserver

Deployment
----------

For information on how to deploy a Django application see the [official documentation](https://docs.djangoproject.com/en/dev/howto/deployment/).

Contributing
------------

If you want to contribute to the development of YADG please use the standard *Fork & Pull* model used on Github. More information on how to apply this model in practice can be found [here](https://help.github.com/articles/using-pull-requests/).

If you want to add a new scraper please also add test cases for the most common album types.

To build the test cases you can use `descgen.visitor.misc.SerializeVisitor` to serialize any instance of a class from the `descgen.result` module.

Use it like this:

```python
from descgen.result import ReleaseResult
from descgen.visitor.misc import SerializeVisitor

r = ReleaseResult()
v = SerializeVisitor(var_name='expected')

print v.visit(r)
```