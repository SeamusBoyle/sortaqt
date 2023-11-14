#!/usr/bin/env python3
import sys
import xml.etree.ElementTree as ET


def print_help():
    print(
        f"""Usage: {sys.argv[0]} [OPTION] [INPUT-FILE]

  -i  write output to INPUT-FILE, no backup is made
  -u  remove duplicate files with the same prefix and alias

Each option must be speficied separately.""",
        file=sys.stderr,
    )


def load_args(argv):
    # -i    inplace, default output stdout
    # -u    unique
    output = None
    filename = None
    unique = None
    for arg in argv[1:]:
        match arg:
            case "-i":
                output = "inplace"
            case "-u":
                unique = True
            case _:
                assert filename == None  # unknown arg or multiple files specified
                filename = arg
    return output, filename, unique


def extract_elem_attr_key(elem, attrs):
    attrs_vals = []
    for attr in attrs:
        val = elem.attrib.get(attr)
        attrs_vals.append(f'{val or ""}')
    return tuple(attrs_vals)


def extract_qresource_elem_attr_key(elem):
    known_attrs = ["prefix", "lang"]
    return extract_elem_attr_key(elem, known_attrs)


def extract_file_elem_attr_key(elem):
    # the "empty" attribute is intentionally ignored
    known_attrs = ["alias"]
    return extract_elem_attr_key(elem, known_attrs)


def extract_file_elem_sort_key(elem):
    return (elem.text, extract_file_elem_attr_key(elem))


def uniq_file_elems(file_elems):
    seen = set()
    uniq_items = []
    for file_elem in file_elems:
        key = extract_file_elem_sort_key(file_elem)
        if key not in seen:
            seen.add(key)
            uniq_items.append(file_elem)
    return uniq_items


def main(argv):
    if len(argv) <= 1:
        print_help()
        return 1
    output, filename, unique = load_args(argv)

    tree = ET.parse(filename)
    root = tree.getroot()

    root[:] = sorted(root, key=lambda e: extract_qresource_elem_attr_key(e))

    for child in root.iter("qresource"):
        file_elems = uniq_file_elems(child) if unique else child
        child[:] = sorted(file_elems, key=extract_file_elem_sort_key)

    ET.indent(tree, space="    ", level=0)
    if output == "inplace":
        tree.write(filename, "unicode")
    else:
        print(ET.tostring(root, "unicode"))
    return 0


if __name__ == "__main__":
    exit(main(sys.argv))
