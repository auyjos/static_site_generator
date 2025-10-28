import unittest

from inline_markdown import (extract_markdown_images, extract_markdown_links,
                             split_nodes_delimiter)
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_split_code_single(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ]
        )
    
    def test_split_bold_single(self):
        node = TextNode("This is text with a **bold phrase** in the middle", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("bold phrase", TextType.BOLD),
                TextNode(" in the middle", TextType.TEXT),
            ]
        )
    
    def test_split_italic_single(self):
        node = TextNode("This is text with an *italic word* here", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("italic word", TextType.ITALIC),
                TextNode(" here", TextType.TEXT),
            ]
        )
    
    def test_split_multiple_delimiters(self):
        node = TextNode("Code `block1` and `block2` here", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("Code ", TextType.TEXT),
                TextNode("block1", TextType.CODE),
                TextNode(" and ", TextType.TEXT),
                TextNode("block2", TextType.CODE),
                TextNode(" here", TextType.TEXT),
            ]
        )
    
    def test_split_no_delimiter(self):
        node = TextNode("This is plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [TextNode("This is plain text", TextType.TEXT)])
    
    def test_split_delimiter_at_start(self):
        node = TextNode("**Bold** text here", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("Bold", TextType.BOLD),
                TextNode(" text here", TextType.TEXT),
            ]
        )
    
    def test_split_delimiter_at_end(self):
        node = TextNode("Text here is **bold**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("Text here is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
            ]
        )
    
    def test_split_entire_text(self):
        node = TextNode("**all bold**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [TextNode("all bold", TextType.BOLD)])
    
    def test_split_non_text_node(self):
        node = TextNode("Already bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [TextNode("Already bold", TextType.BOLD)])
    
    def test_split_multiple_nodes(self):
        nodes = [
            TextNode("First `code` here", TextType.TEXT),
            TextNode("Already bold", TextType.BOLD),
            TextNode("Second `code` here", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("First ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" here", TextType.TEXT),
                TextNode("Already bold", TextType.BOLD),
                TextNode("Second ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" here", TextType.TEXT),
            ]
        )
    
    def test_split_unmatched_delimiter_raises(self):
        node = TextNode("This has `unmatched delimiter", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)


class TestExtractMarkdown(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    
    def test_extract_markdown_images_multiple(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")
            ],
            matches
        )
    
    def test_extract_markdown_images_none(self):
        text = "This is text with no images"
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)
    
    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)
    
    def test_extract_markdown_links_multiple(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev")
            ],
            matches
        )
    
    def test_extract_markdown_links_none(self):
        text = "This is text with no links"
        matches = extract_markdown_links(text)
        self.assertListEqual([], matches)
    
    def test_extract_markdown_links_with_images(self):
        text = "Text with ![image](https://i.imgur.com/zjjcJKZ.png) and [link](https://www.boot.dev)"
        matches = extract_markdown_links(text)
        # Should only extract the link, not the image
        self.assertListEqual([("link", "https://www.boot.dev")], matches)
    
    def test_extract_markdown_images_with_links(self):
        text = "Text with [link](https://www.boot.dev) and ![image](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_images(text)
        # Should only extract the image, not the link
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)


if __name__ == "__main__":
    unittest.main()