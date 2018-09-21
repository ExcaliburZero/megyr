def validate_config(config):
    errors = []

    assert_to_list(errors, "input" in config, "[no_input] Could not find \"input\" section in config. \"input\" section must be present in order to run MESA or GYRE.")
    assert_to_list(errors, "output" in config, "[no_output] Could not find \"output\" section in config. \"output\" section must be present in order save the results of MESA and GYRE.")
    assert_to_list(errors, "stages" in config, "[no_stages] Could not find \"stages\" section in config. \"stages\" section must be present in order to run MESA or GYRE.")

    assert_to_list(errors, nested_in(config, ["output", "output_dir"]), "[no_output_dir] Could not find \"output_dir\" setting in the \"output\" section in config. \"output_dir\" setting must be present in order save the results of MESA and GYRE.")

    assert_to_list(errors, nested_in(config, ["input", "mesa_configs"]), "[no_mesa_configs] Could not find \"mesa_configs\" setting in \"input\" section in config. The \"mesa_configs\" setting must be present in order to run MESA.")

    if should_run_gyre(config):
        assert_to_list(errors, nested_in(config, ["stages", "gyre_params"]), "[no_gyre_params] Could not find \"gyre_params\" setting in \"stages\" section of config. GYRE is set to run, but needs this setting to know what value combinations to try.")

        assert_to_list(errors, nested_in(config, ["settings", "gyre_location"]), "[no_gyre_location] Could not find \"gyre_location\" setting in \"settings\" section of config. GYRE is set to run, but needs this setting to know where the GYRE executable is.")

        assert_to_list(errors, nested_in(config, ["output", "gyre_oscillations_summary_file"]), "[no_gyre_summary_file] Could not find \"gyre_oscillations_summary_file\" setting in \"output\" section of config. GYRE is set to run, but Megyr needs this setting to know where to output the summary of the GYRE oscillation summary files.")
    else:
        # Check for GYRE settings present when GYRE is not set to run
        gyre_missing_msg = "[gyre_not_enabled] Found \"{}\" setting in \"{}\" section of config even though GYRE is not enabled. \"gyre_config\" in the \"input\" section must be specified in order to run GYRE."
        assert_to_list(errors, not nested_in(config, ["output", "gyre_oscillations_summary_file"]), gyre_missing_msg.format("gyre_oscillations_summary_file", "output"))
        assert_to_list(errors, not nested_in(config, ["settings", "gyre_location"]), gyre_missing_msg.format("gyre_location", "settings"))
        assert_to_list(errors, not nested_in(config, ["settings", "gyre_mp_threads"]), gyre_missing_msg.format("gyre_mp_threads", "settings"))
        assert_to_list(errors, not nested_in(config, ["stages", "gyre_params"]), gyre_missing_msg.format("gyre_params", "stages"))
        assert_to_list(errors, not nested_in(config, ["stages", "gyre_derived"]), gyre_missing_msg.format("gyre_derived", "stages"))

    return errors

def assert_to_list(errors, condition, message):
    if not condition:
        errors.append((message))

def should_run_gyre(config):
    return nested_in(config, ["input", "gyre_config"])

def nested_in(config, nested_keys):
    for key in nested_keys:
        if key in config:
            config = config[key]
        else:
            return False

    return True
