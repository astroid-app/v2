def convert_keys_to_dotted(json_data, parent_key=""):
    dotted_dict = {}
    for key, value in json_data.items():
        if isinstance(value, dict):
            dotted_dict.update(convert_keys_to_dotted(value, f"{parent_key}{key}."))
        else:
            dotted_dict[f"{parent_key}{key}"] = value
    return dotted_dict


print(convert_keys_to_dotted({"a": {"b": {"c": 1}}}))