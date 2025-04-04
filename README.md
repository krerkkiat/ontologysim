Ontologysim: a Owlready2 library for applied production simulation
=====================================================================

Ontologysim is an open-source deep production simulation framework, with an emphasis on modularized flexible library design and straightforward usability for applications in research and practice. Ontologysim is built on top of Owlready2 framework and requires Python >3.7.

Ontologysim follows a set of high-level design choices which differentiate it from other similar libraries:

* the simulation can be saved at any time and started from a defined point
* high degrees of freedom and possibilities due to the ontology

## Table of Contents
1. [Installation](#installation)
2. [First Start](#first-start)
3. [Flask](#flask)


Installation
==============

pip
-----------

An unstable version of Production simulation is periodically updated on pyPi and installed as follows:

````bash
pip install 'ontologysim@git+https://github.com/krerkkiat/ontologysim.git'
````

github
-----------

An unstable version of Production simulation is periodically updated on the main branch and
can be installed as follows:

````bash
git clone https://github.com/krerkkiat/ontologysim.git
cd ontologysim
uv sync
````



First Start
===============

Go to the ``/example/Main.py`` and run this python file.

Flask
==============

````bash
mkdir simulation-working-dir
cd simulation-working-dir
python -m ontologysim serve
````

You can then visit ``http://localhost:5000/api/docs`` for the API documentation. The result from the simulation will be store
in the ``simulation-working-dir``.

Problem handling
==================

Owlready2.0
---------------
**Java Path**

Please add the ``bin`` folder of the JRE (or JDK) to the ``PATH`` environment variable.

**Java Memory**

if this error occurs

````bash
owlready2.base.OwlReadyJavaError: Java error message is:
Error occurred during initialization of VM
Could not reserve enough space for 2048000KB object heap
````

then you need to reduce the java memory

1. got to "site-packages\owlready2\reasoning.py"
2. reduce the Java Memory variable to 500


**How to check if everything works**

run in the example folder the `Main.py`