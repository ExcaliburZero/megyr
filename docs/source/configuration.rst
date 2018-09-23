Configuration
=============

.. contents::

Input
-----

mesa_configs
^^^^^^^^^^^^
``list[str]``

The MESA configuration file mustache templates for Megyr to use when running MESA.

* Examples

  * ``["inlist.mustache", "inlist_project.mustache"]``

gyre_config
^^^^^^^^^^^
``str`` - [Optional]

The GYRE configuration file mustache template to use. If this value is provided, then Megyr will run GYRE against the models outputted by MESA.

* Default

  * ``None``

* Examples

  * ``"gyre.in.mustache"``

.. Note::

  If you do not specify a value for ``gyre_config`` then Megyr will not run GYRE.

Output
------

output_dir
^^^^^^^^^^
``str`` - [Optional]

The directory that Megyr will place all of the temporary and output files and directories into. The directory should be specified as a relative path from the directory that the Megyr script is run in.

  * Default

    *  ``out``

mesa_profile_summary_file
^^^^^^^^^^^^^^^^^^^^^^^^^
``str`` - [Optional]

Tells Megyr to output a summary of the MESA profile files for each model as a csv file.

  * Default

    * ``None``

  * Examples

    * ``mesa_profile_attributes.csv``

Settings
--------

mesa_star_location
^^^^^^^^^^^^^^^^^^
``str`` - [Optional]

The path to the MESA ``star`` executable that Megyr will use to run MESA.

  * Default

    * ``star``

gyre_location
^^^^^^^^^^^^^
``str`` - [Optional]

The path to the GYRE execuatable that Megyr will use to run GYRE.

  * Default

    * ``$GYRE_DIR/bin/gyre``

mesa_mp_threads
^^^^^^^^^^^^^^^
``int`` - [Optional]

The number of Open MP threads to have MESA use.

  * Default

    * ``$OMP_NUM_THREADS``

  * Examples

    * ``4``

Stages
------
