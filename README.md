Ontologysim: a Owlready2 library for applied production simulation
=====================================================================

Ontologysim is an open-source deep production simulation framework, with an emphasis on modularized flexible library design and straightforward usability for applications in research and practice. Ontologysim is built on top of Owlready2 framework and requires Python >= 3.9.

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

An unstable version can be installed as follows:

````bash
pip install 'ontologysim@git+https://github.com/krerkkiat/ontologysim.git'
````

github
-----------

An unstable version can be installed as follows:

````bash
git clone https://github.com/krerkkiat/ontologysim.git
cd ontologysim
uv sync
````

This will also give access to the ``example/`` folder.

First Start
===============

1. Make a folder to keep the simulation configuration files.

````bash
mkdir simulation-working-dir
````

2. Create these files in said folder.

````ini
# controller_config.ini
[Controller]
machine = {'type': 'ontologysim.ProductionSimulation.controller:MachineController_FIFO', 'add': {}}
transporter = {'type': 'ontologysim.ProductionSimulation.controller:TransporterController_Hybrid', 'add': {'ontologysim.ProductionSimulation.controller:TransporterController_FIFO': 0.43539036099361705, 'ontologysim.ProductionSimulation.controller:TransporterController_NJF': 0.6759958569333095, 'ontologysim.ProductionSimulation.controller:TransporterController_EDD': 0.5773536432743988}}
orderrelease = {'type':'ontologysim.ProductionSimulation.controller:OrderReleaseControllerEqual','add':{},'fillLevel':0.5}
service_machine = {'type':'ontologysim.ProductionSimulation.controller:ServiceControllerMachine','add':{}}
service_transporter = {'type':'ontologysim.ProductionSimulation.controller:ServiceControllerTransporter','add':{}}
````

````ini
# owl_config.ini
[OWL]
owl_save_path=[{'type':"production_without_task_defect",'save':False,'path':"owl/production_without_task_defect.owl"},
                {'type':"production",'save':False,'path':"owl/production.owl"}
                ]
````

````ini
# logger_config_lvl3.ini
[Type]
type = 'lvl3'

[KPIs]
time_interval=100
log_summary=True
log_time=True
log_events=False
path="log/"


[ConfigIni]
addIni=False
path="config/"

[Plot]
plot=False
number_of_points_x=15
#max 3 values
data=[{'object_name':'all','kpi':'AE','type':'machine'},{'object_name':'all','kpi':'AUITp','type':'transporter'},{'object_name':'all','kpi':'AOET','type':'product'}]

[Save]
csv = False
database = False
````

If you want to also specify the plot configuration, you can create this file

````ini
# plot_log.ini
[Log]
save_dir="plot/"
#supported: formats eps, pdf, pgf, png, ps, raw, rgba, svg, svgz
file_type=['png','svg','pdf']

[Style]
colormap="Accent"
marker=['','o','r']

[LinePlot]
#without object name all
y_data=[{'kpi':'AE','type':'machine','object_name':['m0','all']},{'kpi':'FillLevel','type':'queue'}]

[MultipleLinePlot]
#max 3 kpis
settings=[{'title':"compare some parameters",'data':[{'kpi':'AE','type':'machine','object_name':['m0','all']},{'kpi':'FE','type':'transporter'}]}]


[ScatterPlot]
x_data=[{'kpi':'AE','type':'machine','object_name':'m1'},{'kpi':'A','type':'machine','object_name':'m1'}]
y_data=[{'kpi':'AE','type':'machine','object_name':'m0'},{'kpi':'A','type':'machine','object_name':'m0'}]
````

3. Run the simulation

````bash
cd simulation-working-dir
python -m ontologysim run ./production_config_lvl3.ini ./controller_config.ini ./owl_config.ini ./logger_config_lvl3.ini
````

You can add ``--plot-config ./plot_log.ini`` if you want to also produce the plot.

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