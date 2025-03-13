def yield_differences(a: dict, b: dict, parent: str = ""):
    all_keys = set(a.keys()).union(set(b.keys()))
    for key in all_keys:
        full_key = f"{parent}.{key}" if parent != "" else key

        a_value = a.get(key, "_NO VALUE_")
        b_value = b.get(key, "_NO VALUE_")

        if a_value == b_value:
            continue

        if isinstance(a_value, dict) and isinstance(b_value, dict):
            yield from yield_differences(a_value, b_value, full_key)
            continue

        if isinstance(a_value, list) and isinstance(b_value, list):
            for i, t_zip in enumerate(zip(a_value, b_value)):
                full_arr_key = f"{full_key}.{i}"
                arr_a, arr_b = t_zip
                if arr_a == arr_b:
                    continue

                if arr_a is None or arr_b is None:
                    yield full_arr_key, arr_a, arr_b
                    continue

                if isinstance(arr_a, dict) and isinstance(arr_b, dict):
                    yield from yield_differences(arr_a, arr_b, full_arr_key)
                    continue

                yield full_arr_key, arr_a, arr_b
            continue

        yield full_key, a_value, b_value
