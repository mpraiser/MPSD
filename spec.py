from typing import Optional

from section import Section, SizePolicy, byte


def is_valid_section(section: str):
    return not section.startswith("_")


def is_variable_section(section: str):
    return section.startswith("@")


def load(root_spec: dict, root_label: str = "") -> Section:
    """Parse a spec dict to a Tree"""
    PROPERTIES = "_properties"

    def __spec_parse(spec: dict, label: str, parent: Optional[Section]) -> Section:
        if PROPERTIES not in spec:
            # raise SpecParseError(f"{PROPERTIES} is not found.")
            prop = {}
        else:
            prop = spec[PROPERTIES]

        # unit = prop["unit"]
        unit = byte

        if "size" not in prop:
            size = SizePolicy.auto
        else:
            size = prop["size"]

        if "handler" in prop:
            handler = prop["handler"]
        else:
            handler = None

        if is_variable_section(label):
            list_len = prop["list_len"]
        else:
            list_len = None

        node = Section(
            label, None, unit, size, handler,
            list_len=list_len, parent=parent,
            is_variable_section=is_variable_section(label)
        )

        for child_label in spec:
            if child_label == PROPERTIES:
                continue
            child = __spec_parse(spec[child_label], child_label, node)
            if node.is_variable_section:
                node.add_sub_section_template(child)
            else:
                node.add_child(child)
        return node

    root = __spec_parse(root_spec, root_label, None)
    # preprocess on dependency
    # for section in root.preorder():
    #     if isinstance(section.size, DependencySpec):
    #         d_handler, d_name = section.size
    #         d = root.find(d_name)
    #         section.size = DependencySpec(d_handler, d)
    return root
