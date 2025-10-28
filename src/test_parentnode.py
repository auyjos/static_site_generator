import unittest

from leafnode import LeafNode
from parentnode import ParentNode


class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    
    def test_to_html_multiple_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )
    
    def test_to_html_with_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "container"})
        self.assertEqual(
            parent_node.to_html(),
            '<div class="container"><span>child</span></div>'
        )
    
    def test_to_html_no_tag_raises(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode(None, [child_node])
        with self.assertRaises(ValueError) as context:
            parent_node.to_html()
        self.assertIn("tag", str(context.exception).lower())
    
    def test_to_html_no_children_raises(self):
        parent_node = ParentNode("div", None)
        with self.assertRaises(ValueError) as context:
            parent_node.to_html()
        self.assertIn("children", str(context.exception).lower())
    
    def test_to_html_nested_parents(self):
        leaf1 = LeafNode("a", "Link", {"href": "https://www.google.com"})
        leaf2 = LeafNode(None, " and ")
        leaf3 = LeafNode("b", "bold")
        parent1 = ParentNode("p", [leaf1, leaf2, leaf3])
        parent2 = ParentNode("div", [parent1])
        self.assertEqual(
            parent2.to_html(),
            '<div><p><a href="https://www.google.com">Link</a> and <b>bold</b></p></div>'
        )
    
    def test_to_html_many_children(self):
        children = [
            LeafNode("span", f"Child {i}")
            for i in range(5)
        ]
        parent_node = ParentNode("div", children)
        expected = "<div>" + "".join([f"<span>Child {i}</span>" for i in range(5)]) + "</div>"
        self.assertEqual(parent_node.to_html(), expected)


if __name__ == "__main__":
    unittest.main()