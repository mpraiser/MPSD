from section import Section, SizePolicy, DependencySpec, ListLenPolicy


def parse_non_leaf(section: Section, raw: bytes) -> int:
    used = 0

    if isinstance(section.size, int):
        section.raw = raw[:section.size]
        for child in section.children:
            used += parse(child, section.raw[used:])
        if used < section.size:
            print(f"Warning, raw not all used.")
        used = section.size

    elif isinstance(section.size, DependencySpec):
        section.handle_size_dependency()
        section.raw = raw[:section.size]
        for child in section.children:
            used += parse(child, section.raw[used:])
        if used < section.size:
            print(f"Warning, raw not all used.")
        used = section.size

    elif isinstance(section.size, SizePolicy):
        policy = section.size
        if policy == SizePolicy.auto:
            for child in section.children:
                child: Section
                used += parse(child, raw[used:])
            section.size = used
            section.raw = raw[:used]
        elif policy == SizePolicy.greedy:
            raise Exception(f"Section '{section.label}' unsupported size policy: {policy}")
        else:
            raise Exception(f"Section '{section.label}' unsupported size policy: {policy}")

    else:
        raise Exception(f"Section '{section.label}' unsupported size type: {type(section.size)}")

    return used


def parse_leaf(section: Section, raw: bytes) -> int:
    # step 1: set raw
    if isinstance(section.size, int):
        section.raw = raw[:section.size]
        used = section.size

    elif isinstance(section.size, SizePolicy):
        policy = section.size
        if policy == SizePolicy.auto:
            raise Exception(f"Size of leaf section '{section.label}' cannot be auto!")
        elif policy == SizePolicy.greedy:
            section.raw = raw
            used = len(raw)
        else:
            raise Exception(f"Section '{section.label}' unsupported size policy: {policy}")

    elif isinstance(section.size, DependencySpec):
        section.handle_size_dependency()
        section.raw = raw[:section.size]
        used = section.size

    else:
        raise Exception(f"Section '{section.label}' unsupported size type: {type(section.size)}")

    # step 2: parse value
    section.value = section.handler(section.raw)

    return used


def parse_variable(section: Section, raw: bytes) -> int:
    assert section.is_variable_section
    used = 0
    list_len = 0
    if isinstance(section.list_len, int):
        max_list_len = section.list_len
    elif isinstance(section.list_len, ListLenPolicy):
        policy = section.list_len
        if policy == ListLenPolicy.greedy:
            max_list_len = None
        else:
            raise Exception(f"Section '{section.label}' unsupported list len policy: {policy}")
    else:
        raise Exception(f"Section '{section.label}' unsupported list len type: {type(section.size)}")

    while used < len(raw) and ((not max_list_len) or max_list_len and list_len <= max_list_len):
        sub_section = section.create_sub_section()
        size = parse(sub_section, raw[used:])
        used += size
        section.add_child(sub_section)
        list_len += 1
    section.list_len = list_len
    return used


def parse(section: Section, raw: bytes) -> int:
    """
    :param section:
    :param raw:
    :return: number of bytes used
    """

    if section.is_variable_section:
        return parse_variable(section, raw)

    if section.is_leaf():
        return parse_leaf(section, raw)
    else:
        return parse_non_leaf(section, raw)
