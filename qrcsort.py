#!/usr/bin/env python3
import argparse
import sys
import xml.etree.ElementTree as ET


def load_args(argv):
    parser = argparse.ArgumentParser(
        description="Write sorted Qt resource (.qrc) file contents to standard output",
        add_help=False,  # help arg added manually so it's displayed last in help text
    )
    parser.add_argument(
        "-i", help="write output to INPUT-FILE, no backup is made", action="store_true"
    )
    parser.add_argument(
        "-u",
        help="remove duplicate files with the same prefix and alias",
        action="store_true",
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        metavar="INPUT-FILE",
    )
    parser.add_argument(
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="display this help message and exit",
    )
    args = parser.parse_args(argv[1:])

    output = None
    if args.i:
        output = "inplace"
    filename = args.input_file.name if output == "inplace" else args.input_file
    unique = args.u
    assert (
        output != "inplace" or args.input_file.name != "<stdin>"
    ), "can't write in-place to standard input"
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
    output, filename, unique = load_args(argv)

    tree = ET.parse(filename)
    root = tree.getroot()

    root[:] = sorted(root, key=extract_qresource_elem_attr_key)

    for child in root.iter("qresource"):
        file_elems = uniq_file_elems(child) if unique else child
        child[:] = sorted(file_elems, key=extract_file_elem_sort_key)

    ET.indent(tree, space="    ", level=0)
    # For newline at end of file
    root.tail = root.tail + "\n" if root.tail else "\n"

    if output == "inplace":
        out_file_of_filename = filename
    else:
        out_file_of_filename = sys.stdout

    tree.write(out_file_of_filename, "unicode")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
