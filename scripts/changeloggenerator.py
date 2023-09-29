"""Module to autogenerate the CHANGELOG.rst from GitHub Release Notes."""

from sphinx_github_changelog import changelog

import argparse
import docutils.utils as du
import docutils.nodes as dn

option_spec = {
    "changelog-url": "https://python-ring-doorbell.readthedocs.io/en/stable/#changelog",
    "github": "https://github.com/tchellomello/python-ring-doorbell/releases/",
    "pypi": "https://pypi.org/project/python-ring-doorbell/",
}

OUTPUT_FILENAME = "CHANGELOG.rst"


class NodeVisitor(dn.SparseNodeVisitor):
    """Very basic class to output rst from docutils xml"""

    output = ""

    def output_reference(refuri, reftext):
        return "`" + reftext + " <" + refuri + ">`__ "

    def visit_section(self, node):
        pass

    def visit_title(self, node):
        title = node.astext()
        line = "=" * len(title)
        self.output += "\n\n" + node.astext() + "\n" + line + "\n\n"

    def visit_paragraph(self, node):
        for childnode in node.children[0].children:
            if type(childnode) == dn.reference:
                self.output += NodeVisitor.output_reference(
                    childnode.attributes["refuri"], childnode.children[0].astext()
                )
            else:
                self.output += childnode.astext()

    def visit_raw(self, node):
        theraw = "      " + node.astext()
        self.output += (
            "\n\n.. raw:: html\n\n   <embed>\n"
            + "      ".join(theraw.splitlines(True))
            + "\n   </embed>\n\n"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Change Log Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "token",
        type=str,
        help="Enter GitHub Access Token (from https://github.com/"
        + "settings/tokens/new?description=GitHub%20Changelog%20Generator%20token)",
    )

    args = parser.parse_args()

    doctree = changelog.compute_changelog(args.token, option_spec)

    doc = du.new_document("foo")
    doc.insert(0, doctree)
    nv = NodeVisitor(doc)
    for item in doctree:
        item.walk(nv)

    finaloutput = "=========\nChangelog\n=========\n\n" + nv.output
    with open(OUTPUT_FILENAME, "w") as text_file:
        text_file.write(finaloutput)


if __name__ == "__main__":
    main()
