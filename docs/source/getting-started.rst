Getting started
===============

This tutorial will walk you through running Megyr on a grid of parameters for MESA and GYRE. It assumes that you have some familiarity with how to configure and run MESA and GYRE.

Pre-requisites
--------------

Before starting this tutorial, you should make sure to install ``pipenv`` and ``pyenv``. These tool are not required to use Megyr, but they make using it a lot easier since they can make sure that you are using the correct Python version.

Setting up a project
--------------------

To get started, we will first need to create a new project directory to work in. To run MESA we will need some of the files that the MESA project template has, so we can create a copy of that by running the following commands in the terminal. ::

    cp -r $MESA_DIR/star/work megyr-tutorial
    cd megyr-tutorial

Now that we have a directory we can work in, we'll want to setup a ``pipenv`` environment with a Python 3 installation and install ``megyr``. ::

    pipenv --python 3.6
    pipenv install megyr

Next we will want to create the Python script for using Megyr. To do this, we can create a file called ``megyr_config.py`` with the following code. ::

    import megyr

    def main():
        megyr.run({
            "input": {
                "mesa_configs": ["inlist.mustache"]
            },
            "output": {
                "mesa_profile_summary_file": "mesa_profile_attributes.csv"
            },
            "stages": {
                "mesa_params": {
                    "initial_mass": [1, 1.1, 1.5]
                }
            }
        })

    if __name__ == "__main__":
        main()

For now we will just be running MESA against 3 models, with initial masses of ``1``, ``1.1``, and ``1,5`` M_sun. We will be using one inlist config file for MESA, and output summaries of the profile files that MESA generates.

MESA
----

Now that we have our script to run MESA, we will need to get the executable to use to run MESA and the configuration file to run MESA on.

Since we created our project from the MESA project template, we can run the following command to compile the MESA ``star`` executable. ::

    ./mk

Next we will want to setup the MESA inlist configuration file to use. By default the MESA project template gives us three inlist files, but for now we will remove them to replace them with a simpler one. ::

    rm inlist inlist_pgstar inlist_project

Now we will create the inlist file we will use. Megyr allows you to provide uses mustache templates for configuration files which it will fill in the parameter values of at runtime. So we can create a file called ``inlist.mustache`` with the following contents. ::

    &star_job

      ! begin with a pre-main sequence model
        create_pre_main_sequence_model = .true.

    / !end of star_job namelist


    &controls

      ! starting specifications
        initial_mass = {{initial_mass}} ! in Msun units

      ! stop at 2 Gyr
        max_age = 2000000000

    / ! end of controls namelist

You can see that for the ``initial_mass`` we are setting it to ``{{initial_mass}}``. Since this is a mustache template, Megyr will fill in any instance of ``{{some_variable}}`` with the value of the name that is inside of the two curly braces.

We can then execute our Megyr script by running the following command in the terminal. ::

    pipenv run python megyr_config.py

You should then see output appear in the terminal from the MESA runs. Wait for the MESA runs for all three models to complete. You can then take a look at the files that MESA and Megyr outputted by running the following commands. ::

    ls out
    ls out/mesa_initial_mass_1__
    less out/mesa_initial_mass_1__/mesa_profile_attributes.csv

The ``mesa_profile_attributes.csv`` files that we had Megyr create for each model contain summary information from all of the profile files that MESA outputted.

Now, if you try to rerun the Megyr script you will see one of the nice features of Megyr. ::

    pipenv run python megyr_config.py

You will notice that the MESA runs are not repeated, since Megyr notices that they have already been run. Megyr will keep the results from MESA and GYRE runs, and for any run that completed, Megyr will not rerun it and will instead work on the next task that has not yet been completed.
