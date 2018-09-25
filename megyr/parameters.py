def create_grid(values, rows, params):
    processed_params = process_params(values, rows, params)

    combinations = generate_param_combinations(processed_params)

    return combinations

def process_params(values, rows, raw_params):
    params = {}
    for key in raw_params:
        value = raw_params[key]

        if isinstance(value, list):
            params[key] = set(value)
        elif isinstance(value, dict):
            assert("type" in value)
            if value["type"] == "where":
                assert("check" in value)
                assert("then" in value)

                assert(
                    "gte" in value or "gt" in value or
                    "lte" in value or "lt" in value or
                    "eq" in value
                )

                assert(value["check"] in rows.columns)
                assert(value["then"] in rows.columns)

                check = value["check"]
                then = value["then"]

                rows_filtered = rows
                if "gte" in value:
                    rows_filtered = rows_filtered[rows_filtered[check] >= value["gte"]]
                if "gt" in value:
                    rows_filtered = rows_filtered[rows_filtered[check] > value["gt"]]
                if "lte" in value:
                    rows_filtered = rows_filtered[rows_filtered[check] <= value["lte"]]
                if "lt" in value:
                    rows_filtered = rows_filtered[rows_filtered[check] < value["lt"]]
                if "eq" in value:
                    rows_filtered = rows_filtered[rows_filtered[check] == value["eq"]]

                params[key] = set(rows_filtered[then])
            else:
                raise Exception()
        else:
            params[key] = set(value)

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

