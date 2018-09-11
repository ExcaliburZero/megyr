def create_grid(data, params):
    processed_params = process_params(params)

    combinations = generate_param_combinations(processed_params)

    return combinations

def process_params(raw_params):
    params = {}
    for key in raw_params:
        value = raw_params[key]

        if isinstance(value, list):
            params[key] = value
        elif isinstance(value, dict):
            assert ("start" in value)
            assert ("end" in value)

            params[key] = list(range(value["start"], value["end"] + 1))

    return params

def generate_param_combinations(params):
    remaining = list(params.keys())
    chosen = {}
    combinations = []

    generate_param_combinations_h(params, remaining, chosen, combinations)

    return combinations

def generate_param_combinations_h(params, remaining, chosen, combinations):
    if len(remaining) == 0:
        combinations.append(chosen)

        return None

    p = remaining[0]
    for v in params[p]:
        new_chosen = dict(chosen)

        new_chosen[p] = v

        generate_param_combinations_h(params, remaining[1:], new_chosen, combinations)

