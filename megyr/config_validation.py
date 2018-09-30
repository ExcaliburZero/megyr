def validate_config(config):
    errors = []

    assert_to_list(errors, "input" in config, "[no_input] Could not find \"input\" section in config. \"input\" section must be present in order to run MESA or GYRE.")
    assert_to_list(errors, "stages" in config, "[no_stages] Could not find \"stages\" section in config. \"stages\" section must be present in order to run MESA or GYRE.")

    assert_to_list(errors, nested_in(config, ["input", "mesa_configs"]), "[no_mesa_configs] Could not find \"mesa_configs\" setting in \"input\" section in config. The \"mesa_configs\" setting must be present in order to run MESA.")

    if should_run_gyre(config):
        assert_to_list(errors, nested_in(config, ["stages", "gyre_params"]), "[no_gyre_params] Could not find \"gyre_params\" setting in \"stages\" section of config. GYRE is set to run, but needs this setting to know what value combinations to try.")
    else:
        # Check for GYRE settings present when GYRE is not set to run
        gyre_missing_msg = "[gyre_not_enabled] Found \"{}\" setting in \"{}\" section of config even though GYRE is not enabled. \"gyre_config\" in the \"input\" section must be specified in order to run GYRE."
        assert_to_list(errors, not nested_in(config, ["output", "gyre_oscillations_summary_file"]), gyre_missing_msg.format("gyre_oscillations_summary_file", "output"))
        assert_to_list(errors, not nested_in(config, ["settings", "gyre_location"]), gyre_missing_msg.format("gyre_location", "settings"))
        assert_to_list(errors, not nested_in(config, ["settings", "gyre_mp_threads"]), gyre_missing_msg.format("gyre_mp_threads", "settings"))
        assert_to_list(errors, not nested_in(config, ["stages", "gyre_params"]), gyre_missing_msg.format("gyre_params", "stages"))
        assert_to_list(errors, not nested_in(config, ["stages", "gyre_derived"]), gyre_missing_msg.format("gyre_derived", "stages"))

    return errors

def set_defaults(config):
    ### Output
    if not nested_in(config, ["output", "output_dir"]):
        nested_put(config, ["output", "output_dir"], "out")

    if not nested_in(config, ["output", "mesa_profile_summary_file"]):
        nested_put(config, ["output", "mesa_profile_summary_file"], "mesa_profile_attributes.csv")

    ### Settings
    if not nested_in(config, ["settings", "mesa_star_location"]):
        nested_put(config, ["settings", "mesa_star_location"], "star")

    if not nested_in(config, ["settings", "gyre_location"]):
        nested_put(config, ["settings", "gyre_location"], "$GYRE_DIR/bin/gyre")

    if not nested_in(config, ["settings", "gyre_mp_threads"]) and \
            nested_in(config, ["settings", "mesa_mp_threads"]):
        nested_put(config, ["settings", "gyre_mp_threads"], config["settings"]["mesa_mp_threads"])

def assert_to_list(errors, condition, message):
    if not condition:
        errors.append((message))

def should_run_gyre(config):
    return nested_in(config, ["input", "gyre_config"])

def nested_in(config, nested_keys):
    """
    Checks if the given nested keys are within the given dict. Returns false if
    any of the intermediate keys or the final key are not nested in the dict.

    >>> config = {}
    >>> nested_in(config, ["settings", "gyre_mp_threads"])
    False

    >>> config = {"settings": {}}
    >>> nested_in(config, ["settings", "gyre_mp_threads"])
    False

    >>> config = {"settings": {"gyre_mp_threads": 4}}
    >>> nested_in(config, ["settings", "gyre_mp_threads"])
    True
    """
    for key in nested_keys:
        if key in config:
            config = config[key]
        else:
            return False

    return True

def nested_put(config, nested_keys, value):
    """
    Puts the given nested key value pair into the given dict. If any part of
    the nested key structure does not yet exist, then it will be created in the
    process.

    >>> config = {}
    >>> nested_put(config, ["key"], "value")
    >>> config["key"]
    'value'

    >>> config = {}
    >>> nested_put(config, ["settings", "gyre_mp_threads"], 2)
    >>> config["settings"]["gyre_mp_threads"]
    2
    """
    if len(nested_keys) == 0:
        raise Exception("Invalid number of nested keys.")
    if len(nested_keys) == 1:
        config[nested_keys[0]] = value
    else:
        next_key = nested_keys[0]
        if next_key not in config:
            config[next_key] = {}

        nested_put(config[next_key], nested_keys[1:], value)
