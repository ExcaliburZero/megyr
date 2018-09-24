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

gyre_oscillations_ad_summary_file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
``str`` - [Optional]

Tells Megyr to output a summary of the adiabatic oscillation summary files as a csv file. The adiabatic oscillation summary files must be set in the GYRE config template to be outputted to ``{{ad_output_summary_file}}``.

  * Default

    * ``None``

  * Examples

    * ``oscillations_ad.csv``

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

    * Will use the number of threads set in ``$OMP_NUM_THREADS``.

  * Examples

    * ``4``

gyre_mp_threads
^^^^^^^^^^^^^^^
``int`` - [Optional]

The number of Open MP threads to have GYRE use.

  * Default

    * Will use the number of threads set in ``mesa_mp_threads``, or if that is not set then will use the number set in ``$OMP_NUM_THREADS``.

  * Examples

    * ``4``

Stages
------

mesa_params
^^^^^^^^^^^
``dict``

The parameter value possibilities to use to construct the grid of MESA models to run.

  * Examples

  .. code:: python

    # Use 6 models with varying y values and inital masses
    {
        "y": [1.0, 1.2, 2.5],
        "initial_mass": [1, 5]
    }

mesa_derived
^^^^^^^^^^^^
``function[dict, dict]`` - [Optional]

The function to apply to each MESA parameter combination to extract additional values plug into the MESA config templates specified in ``mesa_configs``.

  * Examples

  .. code:: python

    # Add a max age to use that is based on the initial_mass
    def calc_mesa_derived(mesa_params):
        derived = dict(mesa_params)

        initial_mass = mesa_params["initial_mass"]

        mass_lookup = {
            "1": 1000000000,
            "1.5": 500000000
        }

        derived["max_age"] = mass_lookup[str(initial_mass)]

        return derived

gyre_params
^^^^^^^^^^^
``function[dict, pd.DataFrame, dict]`` - [Optional]

The function to apply to the MESA parameter combination and MESA profile data to determine the parameter value possibilities to use to construct the grid of GYRE runs to perform.

  * Examples

  .. code:: python

    # Calculate l=0, l=1, and l=2 oscillations for profiles with a star age greater than 1 Gyr
    def calc_gyre_params(mesa_params, mesa_data):
        return {
            "profile": mesa_data[mesa_data["star_age"] > 1000000000]["profile"]
            "l": [0, 1, 2]
        }

gyre_derived
^^^^^^^^^^^^
``function[dict, pd.DataFrame, dict, dict]`` - [Optional]

The function to apply to each group of MESA parameter combination, MESA profile data, and GYRE parameter combination to extract additional values plug into the GYRE config template specified in ``gyre_config``.

  * Examples

  .. code:: python

    # Use a different frequency range for each l value
    def calc_gyre_derived(mesa_params, mesa_data, gyre_params):
        derived = dict(gyre_params)

        derived["freq_min"] = gyre_params["l"] * 200
        derived["freq_max"] = gyre_params["l"] * 200 + 500

        return derived
