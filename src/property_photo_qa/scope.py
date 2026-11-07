"""Validate explicit review exclusions; callers keep excluded records visible in reports."""
def review_exclusions(value, known):
    if value is None:
        return {}
    if not isinstance(value, dict) or len(value) > 10000:
        raise ValueError("exclusions must be an object with at most 10000 IDs and reasons")
    result = {}
    for key, reason in value.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(reason, str) or not reason.strip() or len(reason) > 500:
            raise ValueError("each excluded ID requires a nonempty reason of at most 500 characters")
        if key not in known:
            raise ValueError("excluded ID not present in this population: " + key)
        result[key] = reason.strip()
    return result
