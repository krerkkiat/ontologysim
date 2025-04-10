Installation
==============

pip
-----------

An unstable version can be installed as follows:

.. code-block:: console

   pip install 'ontologysim@git+https://github.com/krerkkiat/ontologysim.git'


github
-----------

An unstable version can be installed as follows:

.. code-block:: console

   git clone https://github.com/krerkkiat/ontologysim.git
   cd ontologysim
   uv sync



How to check if everything works
---------------------------------------------

run in the example folder the `Main.py`

Additional installation for ubuntu
---------------------------------------------
installation of odbc, java and some other packages

.. code-block:: console

    sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev wget
    sudo apt-get install unixodbc-dev
    sudo apt install default-jre


Problem handling
--------------------

Owlready2.0
~~~~~~~~~~~~

**Java Path**

Please add the ``bin`` folder of the JRE (or JDK) to the ``PATH`` environment variable.

**Java Memory**

if this error occurs

.. code-block:: console

   owlready2.base.OwlReadyJavaError: Java error message is:
   Error occurred during initialization of VM
   Could not reserve enough space for 2048000KB object heap


then you need to reduce the java memory

1. goto "site-packages\owlready2\reasoning.py"
2. reduce the Java Memory variable to 500

Database
~~~~~~~~~~~~

if a database error occurs

1. Check if file in ProductionSimulation/database/SimulationRun.db exist, otherwise create the missing file
2. run CreateDatabase.py in  ProductionSimulation/database