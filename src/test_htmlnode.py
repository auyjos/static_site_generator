import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_multiple(self):
        node = HTMLNode(tag="a", props={
            "href": "https://www.google.com",
            "target": "_blank",
        })
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank"'
        )

    def test_props_to_html_empty(self):
        node = HTMLNode(tag="p", props={})
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_none(self):
        node = HTMLNode(tag="p", props=None)
        self.assertEqual(node.props_to_html(), "")

    def test_repr_has_fields(self):
        child = HTMLNode(tag="span", value="hi")
        node = HTMLNode(tag="p", children=[child], props={"class": "lead"})
        rep = repr(node)
        self.assertIn("HTMLNode(", rep)
        self.assertIn("tag=p", rep)
        self.assertIn("props={'class': 'lead'}", rep)


if __name__ == "__main__":
    unittest.main()
