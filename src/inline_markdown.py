import re

from textnode import TextNode, TextType, text_node_to_html_node


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        parts = old_node.text.split(delimiter)
        if len(parts) % 2 == 0:
            raise ValueError(f"Invalid markdown: unmatched delimiter '{delimiter}'")
        
        for i, part in enumerate(parts):
            if part == "":
                continue

            if i % 2 == 0:
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))
    return new_nodes

def extract_markdown_images(text):
    """
    Extract markdown images from text.
    Returns a list of tuples (alt_text, url).
    """
    pattern = r"!\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches


def extract_markdown_links(text):
    """
    Extract markdown links from text.
    Returns a list of tuples (anchor_text, url).
    """
    pattern = r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)"
    matches = re.findall(pattern, text)
    return matches