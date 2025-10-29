import re
from enum import Enum

from htmlnode import HTMLNode
from leafnode import LeafNode
from parentnode import ParentNode
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

def split_nodes_image(old_nodes):
    """
    Split nodes based on markdown image syntax.
    """
    new_nodes = []
    
    for old_node in old_nodes:
        # If the node is not a text type, just add it as-is
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        # Extract all images from the text
        images = extract_markdown_images(old_node.text)
        
        # If no images, add the node as-is
        if not images:
            new_nodes.append(old_node)
            continue
        
        # Process each image
        remaining_text = old_node.text
        for image_alt, image_url in images:
            # Split the text at the image markdown
            sections = remaining_text.split(f"![{image_alt}]({image_url})", 1)
            
            # Add the text before the image (if not empty)
            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            
            # Add the image node
            new_nodes.append(TextNode(image_alt, TextType.IMAGE, image_url))
            
            # Update remaining text to the part after the image
            remaining_text = sections[1] if len(sections) > 1 else ""
        
        # Add any remaining text after all images
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    
    return new_nodes

def split_nodes_link(old_nodes):
    """
    Split nodes based on markdown link syntax.
    """
    new_nodes = []
    
    for old_node in old_nodes:
        # If the node is not a text type, just add it as-is
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        # Extract all links from the text
        links = extract_markdown_links(old_node.text)
        
        # If no links, add the node as-is
        if not links:
            new_nodes.append(old_node)
            continue
        
        # Process each link
        remaining_text = old_node.text
        for link_text, link_url in links:
            # Split the text at the link markdown
            sections = remaining_text.split(f"[{link_text}]({link_url})", 1)
            
            # Add the text before the link (if not empty)
            if sections[0]:
                new_nodes.append(TextNode(sections[0], TextType.TEXT))
            
            # Add the link node
            new_nodes.append(TextNode(link_text, TextType.LINK, link_url))
            
            # Update remaining text to the part after the link
            remaining_text = sections[1] if len(sections) > 1 else ""
        
        # Add any remaining text after all links
        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))
    
    return new_nodes

def text_to_textnodes(text):
    """
    Convert raw markdown text into a list of TextNode objects.
    Processes bold, italic, code, images, and links.
    """
    # Start with a single text node containing all the text
    nodes = [TextNode(text, TextType.TEXT)]
    
    # Apply all splitting functions in sequence
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)  # Add underscore support for italic
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    
    return nodes

def markdown_to_blocks(markdown):
    """
    Split a markdown document into block-level strings.
    
    Blocks are separated by blank lines (double newlines). Each block is stripped
    of leading/trailing whitespace, and empty blocks are removed.
    
    Args:
        markdown: A string containing the full markdown document
        
    Returns:
        A list of block strings
    """
    # Split on double newlines to get blocks
    blocks = markdown.split("\n\n")
    
    # Strip whitespace from each block and filter out empty blocks
    filtered_blocks = []
    for block in blocks:
        # Strip leading and trailing whitespace
        stripped_block = block.strip()
        # Only add non-empty blocks
        if stripped_block:
            filtered_blocks.append(stripped_block)
    
    return filtered_blocks

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def block_to_block_type(block):
    """
    Determine the type of a markdown block.
    
    Args:
        block: A string containing a single markdown block (with whitespace already stripped)
        
    Returns:
        A BlockType enum value representing the type of block
    """
    lines = block.split("\n")
    
    # Check for heading (1-6 # characters followed by a space)
    if block.startswith("#"):
        # Count the number of # characters at the start
        hash_count = 0
        for char in block:
            if char == "#":
                hash_count += 1
            else:
                break
        
        # Valid heading: 1-6 hashes followed by a space
        if 1 <= hash_count <= 6 and hash_count < len(block) and block[hash_count] == " ":
            return BlockType.HEADING
    
    # Check for code block (starts and ends with ```)
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    
    # Check for quote block (every line starts with >)
    if all(line.startswith(">") for line in lines):
        return BlockType.QUOTE
    
    # Check for unordered list (every line starts with "- ")
    if all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list (lines start with "1. ", "2. ", etc.)
    is_ordered_list = True
    for i, line in enumerate(lines):
        expected_prefix = f"{i + 1}. "
        if not line.startswith(expected_prefix):
            is_ordered_list = False
            break
    
    if is_ordered_list and len(lines) > 0:
        return BlockType.ORDERED_LIST
    
    # Default to paragraph
    return BlockType.PARAGRAPH





def text_to_children(text):
    """
    Convert a string of text with inline markdown into a list of HTMLNode children.
    
    Args:
        text: A string containing text with inline markdown
        
    Returns:
        A list of HTMLNode objects representing the inline elements
    """
    # Convert text to TextNodes (handles bold, italic, code, images, links)
    text_nodes = text_to_textnodes(text)
    
    # Convert each TextNode to an HTMLNode
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    
    return children


def paragraph_to_html_node(block):
    """
    Convert a paragraph block to an HTMLNode.
    """
    # Join lines with spaces and convert to children
    lines = block.split("\n")
    text = " ".join(lines)
    children = text_to_children(text)
    return ParentNode("p", children)


def heading_to_html_node(block):
    """
    Convert a heading block to an HTMLNode.
    """
    # Count the number of # characters
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    
    # Extract the heading text (after the # and space)
    text = block[level + 1:]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    """
    Convert a code block to an HTMLNode.
    Code blocks should not process inline markdown.
    """
    # Remove the ``` from start and end
    if block.startswith("```") and block.endswith("```"):
        code_text = block[3:-3]
    else:
        code_text = block
    
    # Create a text node without processing inline markdown
    code_node = LeafNode("code", code_text)
    return ParentNode("pre", [code_node])


def quote_to_html_node(block):
    """
    Convert a quote block to an HTMLNode.
    """
    lines = block.split("\n")
    # Remove the > from each line
    clean_lines = []
    for line in lines:
        if line.startswith("> "):
            clean_lines.append(line[2:])
        elif line.startswith(">"):
            clean_lines.append(line[1:])
        else:
            clean_lines.append(line)
    
    # Join lines and convert to children
    text = " ".join(clean_lines)
    children = text_to_children(text)
    return ParentNode("blockquote", children)


def unordered_list_to_html_node(block):
    """
    Convert an unordered list block to an HTMLNode.
    """
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        # Remove the "- " prefix
        text = line[2:]
        children = text_to_children(text)
        list_items.append(ParentNode("li", children))
    
    return ParentNode("ul", list_items)


def ordered_list_to_html_node(block):
    """
    Convert an ordered list block to an HTMLNode.
    """
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        # Remove the "1. ", "2. ", etc. prefix
        # Find the first space after the number and period
        space_index = line.index(". ") + 2
        text = line[space_index:]
        children = text_to_children(text)
        list_items.append(ParentNode("li", children))
    
    return ParentNode("ol", list_items)


def markdown_to_html_node(markdown):
    """
    Convert a full markdown document into a single parent HTMLNode.
    
    Args:
        markdown: A string containing the full markdown document
        
    Returns:
        A ParentNode HTMLNode containing all the blocks as children
    """
    # Split markdown into blocks
    blocks = markdown_to_blocks(markdown)
    
    # Convert each block to an HTMLNode
    block_nodes = []
    for block in blocks:
        block_type = block_to_block_type(block)
        
        if block_type == BlockType.PARAGRAPH:
            block_nodes.append(paragraph_to_html_node(block))
        elif block_type == BlockType.HEADING:
            block_nodes.append(heading_to_html_node(block))
        elif block_type == BlockType.CODE:
            block_nodes.append(code_to_html_node(block))
        elif block_type == BlockType.QUOTE:
            block_nodes.append(quote_to_html_node(block))
        elif block_type == BlockType.UNORDERED_LIST:
            block_nodes.append(unordered_list_to_html_node(block))
        elif block_type == BlockType.ORDERED_LIST:
            block_nodes.append(ordered_list_to_html_node(block))
    
    # Return all blocks wrapped in a div
    return ParentNode("div", block_nodes)

def extract_title(markdown):
    """
    Extract the h1 header from a markdown string.
    
    Args:
        markdown: A string containing markdown text
        
    Returns:
        The h1 header text without the # and whitespace
        
    Raises:
        Exception: If no h1 header is found
    """
    lines = markdown.split("\n")
    
    for line in lines:
        # Strip leading/trailing whitespace
        stripped_line = line.strip()
        
        # Check if it starts with a single # followed by a space
        if stripped_line.startswith("# "):
            # Return the title without the # and leading/trailing whitespace
            return stripped_line[2:].strip()
    
    # No h1 header found
    raise Exception("No h1 header found in markdown")