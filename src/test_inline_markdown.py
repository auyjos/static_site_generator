import unittest

from inline_markdown import (BlockType, block_to_block_type,
                             extract_markdown_images, extract_markdown_links,
                             extract_title, markdown_to_blocks,
                             split_nodes_delimiter, split_nodes_image,
                             split_nodes_link, text_node_to_html_node,
                             text_to_textnodes)
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


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )
    
    def test_split_images_single(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )
    
    def test_split_images_at_start(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png) at start",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" at start", TextType.TEXT),
            ],
            new_nodes,
        )
    
    def test_split_images_at_end(self):
        node = TextNode(
            "Text at end ![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Text at end ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )
    
    def test_split_images_none(self):
        node = TextNode("This is text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("This is text with no images", TextType.TEXT)], new_nodes)
    
    def test_split_images_non_text_node(self):
        node = TextNode("Already bold", TextType.BOLD)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("Already bold", TextType.BOLD)], new_nodes)


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )
    
    def test_split_links_single(self):
        node = TextNode(
            "This is text with a [link](https://www.boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.boot.dev"),
            ],
            new_nodes,
        )
    
    def test_split_links_at_start(self):
        node = TextNode(
            "[link](https://www.boot.dev) at start",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("link", TextType.LINK, "https://www.boot.dev"),
                TextNode(" at start", TextType.TEXT),
            ],
            new_nodes,
        )
    
    def test_split_links_at_end(self):
        node = TextNode(
            "Text at end [link](https://www.boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Text at end ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.boot.dev"),
            ],
            new_nodes,
        )
    
    def test_split_links_none(self):
        node = TextNode("This is text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([TextNode("This is text with no links", TextType.TEXT)], new_nodes)
    
    def test_split_links_non_text_node(self):
        node = TextNode("Already bold", TextType.BOLD)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([TextNode("Already bold", TextType.BOLD)], new_nodes)
    
    def test_split_links_with_images(self):
        node = TextNode(
            "Text with ![image](https://i.imgur.com/zjjcJKZ.png) and [link](https://www.boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        # Should split the link but leave the image syntax as text
        self.assertListEqual(
            [
                TextNode("Text with ![image](https://i.imgur.com/zjjcJKZ.png) and ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://www.boot.dev"),
            ],
            new_nodes,
        )

def test_text_to_textnodes_full_example(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )
    
def test_text_to_textnodes_plain_text(self):
    text = "This is just plain text with no formatting"
    nodes = text_to_textnodes(text)
    self.assertListEqual(
        [TextNode("This is just plain text with no formatting", TextType.TEXT)],
        nodes,
    )
    
def test_text_to_textnodes_only_bold(self):
    text = "This has **bold text** here"
    nodes = text_to_textnodes(text)
    self.assertListEqual(
        [
            TextNode("This has ", TextType.TEXT),
            TextNode("bold text", TextType.BOLD),
            TextNode(" here", TextType.TEXT),
        ],
        nodes,
    )

def test_text_to_textnodes_only_italic(self):
    text = "This has *italic text* here"
    nodes = text_to_textnodes(text)
    self.assertListEqual(
        [
            TextNode("This has ", TextType.TEXT),
            TextNode("italic text", TextType.ITALIC),
            TextNode(" here", TextType.TEXT),
        ],
        nodes,
    )

def test_text_to_textnodes_only_code(self):
    text = "This has `code` here"
    nodes = text_to_textnodes(text)
    self.assertListEqual(
        [
            TextNode("This has ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" here", TextType.TEXT),
        ],
        nodes,
    )

def test_text_to_textnodes_only_image(self):
    text = "This has ![image](https://example.com/img.png) here"
    nodes = text_to_textnodes(text)
    self.assertListEqual(
        [
            TextNode("This has ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
            TextNode(" here", TextType.TEXT),
        ],
        nodes,
    )

def test_text_to_textnodes_only_link(self):
    text = "This has [link](https://example.com) here"
    nodes = text_to_textnodes(text)
    self.assertListEqual(
        [
            TextNode("This has ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://example.com"),
            TextNode(" here", TextType.TEXT),
        ],
        nodes,
    )

def test_text_to_textnodes_multiple_formats(self):
    text = "**bold** and *italic* and `code`"
    nodes = text_to_textnodes(text)
    self.assertListEqual(
        [
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ],
        nodes,
    )

def test_text_to_textnodes_nested_bold_italic(self):
    # Note: This tests bold and italic separately, not truly nested
    text = "Start **bold *and italic* text** end"
    nodes = text_to_textnodes(text)
    # The function processes bold first, then italic within the bold sections
    self.assertListEqual(
        [
            TextNode("Start ", TextType.TEXT),
            TextNode("bold ", TextType.BOLD),
            TextNode("and italic", TextType.ITALIC),
            TextNode(" text", TextType.BOLD),
            TextNode(" end", TextType.TEXT),
        ],
        nodes,
    )

def test_text_to_textnodes_image_and_link(self):
    text = "![img](https://img.com) and [link](https://link.com)"
    nodes = text_to_textnodes(text)
    self.assertListEqual(
        [
            TextNode("img", TextType.IMAGE, "https://img.com"),
            TextNode(" and ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://link.com"),
        ],
        nodes,
    )




class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )
    
    def test_markdown_to_blocks_single_block(self):
        md = "This is a single block with no blank lines"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a single block with no blank lines"])
    
    def test_markdown_to_blocks_multiple_newlines(self):
        md = """
First block


Second block



Third block
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["First block", "Second block", "Third block"])
    
    def test_markdown_to_blocks_with_whitespace(self):
        md = """
  First block with leading space  

    Second block with more spaces    
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["First block with leading space", "Second block with more spaces"])
    
    def test_markdown_to_blocks_empty_string(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])
    
    def test_markdown_to_blocks_only_newlines(self):
        md = "\n\n\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])


class TestBlockToBlockType(unittest.TestCase):
    def test_block_to_block_type_heading_h1(self):
        block = "# Heading 1"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    
    def test_block_to_block_type_heading_h2(self):
        block = "## Heading 2"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    
    def test_block_to_block_type_heading_h6(self):
        block = "###### Heading 6"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
    
    def test_block_to_block_type_heading_no_space(self):
        block = "#NoSpace"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_block_to_block_type_heading_too_many_hashes(self):
        block = "####### Too many"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_block_to_block_type_code(self):
        block = "```\ncode here\nmore code\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
    
    def test_block_to_block_type_code_single_line(self):
        block = "```code```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
    
    def test_block_to_block_type_code_missing_end(self):
        block = "```\ncode here"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_block_to_block_type_quote_single_line(self):
        block = "> This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)
    
    def test_block_to_block_type_quote_multi_line(self):
        block = "> Line 1\n> Line 2\n> Line 3"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)
    
    def test_block_to_block_type_quote_missing_marker(self):
        block = "> Line 1\nLine 2\n> Line 3"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_block_to_block_type_unordered_list(self):
        block = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)
    
    def test_block_to_block_type_unordered_list_single(self):
        block = "- Single item"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)
    
    def test_block_to_block_type_unordered_list_missing_marker(self):
        block = "- Item 1\nItem 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_block_to_block_type_unordered_list_no_space(self):
        block = "-NoSpace"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_block_to_block_type_ordered_list(self):
        block = "1. Item 1\n2. Item 2\n3. Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)
    
    def test_block_to_block_type_ordered_list_single(self):
        block = "1. Single item"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)
    
    def test_block_to_block_type_ordered_list_wrong_start(self):
        block = "2. Item 1\n3. Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_block_to_block_type_ordered_list_skip_number(self):
        block = "1. Item 1\n3. Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_block_to_block_type_ordered_list_no_space(self):
        block = "1.NoSpace"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_block_to_block_type_paragraph(self):
        block = "This is just a normal paragraph."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)
    
    def test_block_to_block_type_paragraph_multiline(self):
        block = "This is a paragraph\nwith multiple lines\nof text."
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes_full_example(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )
    
    def test_text_to_textnodes_plain_text(self):
        text = "This is just plain text with no formatting"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [TextNode("This is just plain text with no formatting", TextType.TEXT)],
            nodes,
        )
    
    def test_text_to_textnodes_only_bold(self):
        text = "This has **bold text** here"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This has ", TextType.TEXT),
                TextNode("bold text", TextType.BOLD),
                TextNode(" here", TextType.TEXT),
            ],
            nodes,
        )

    def test_text_to_textnodes_only_italic(self):
        text = "This has *italic text* here"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This has ", TextType.TEXT),
                TextNode("italic text", TextType.ITALIC),
                TextNode(" here", TextType.TEXT),
            ],
            nodes,
        )

    def test_text_to_textnodes_only_code(self):
        text = "This has `code` here"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This has ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" here", TextType.TEXT),
            ],
            nodes,
        )

    def test_text_to_textnodes_only_image(self):
        text = "This has ![image](https://example.com/img.png) here"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This has ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
                TextNode(" here", TextType.TEXT),
            ],
            nodes,
        )

    def test_text_to_textnodes_only_link(self):
        text = "This has [link](https://example.com) here"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("This has ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://example.com"),
                TextNode(" here", TextType.TEXT),
            ],
            nodes,
        )

    def test_text_to_textnodes_multiple_formats(self):
        text = "**bold** and *italic* and `code`"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" and ", TextType.TEXT),
                TextNode("code", TextType.CODE),
            ],
            nodes,
        )

    def test_text_to_textnodes_bold_and_italic_separate(self):
        text = "Start **bold** and *italic* end"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("Start ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" end", TextType.TEXT),
            ],
            nodes,
        )

    def test_text_to_textnodes_image_and_link(self):
        text = "![img](https://img.com) and [link](https://link.com)"
        nodes = text_to_textnodes(text)
        self.assertListEqual(
            [
                TextNode("img", TextType.IMAGE, "https://img.com"),
                TextNode(" and ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://link.com"),
            ],
            nodes,
        )


class TestExtractTitle(unittest.TestCase):
    def test_extract_title_simple(self):
        markdown = "# Hello"
        title = extract_title(markdown)
        self.assertEqual(title, "Hello")
    
    def test_extract_title_with_whitespace(self):
        markdown = "#   Hello World   "
        title = extract_title(markdown)
        self.assertEqual(title, "Hello World")
    
    def test_extract_title_multiline(self):
        markdown = """
Some text before

# My Title

Some text after
"""
        title = extract_title(markdown)
        self.assertEqual(title, "My Title")
    
    def test_extract_title_first_h1_only(self):
        markdown = """
# First Title

## Second heading

# Another H1
"""
        title = extract_title(markdown)
        self.assertEqual(title, "First Title")
    
    def test_extract_title_no_h1_raises(self):
        markdown = "## Only H2\n\nSome text"
        with self.assertRaises(Exception):
            extract_title(markdown)
    
    def test_extract_title_no_space_after_hash(self):
        markdown = "#NoSpace"
        with self.assertRaises(Exception):
            extract_title(markdown)
    
    def test_extract_title_empty_string(self):
        markdown = ""
        with self.assertRaises(Exception):
            extract_title(markdown)

if __name__ == "__main__":
    unittest.main() 