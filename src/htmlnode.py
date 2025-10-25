from typing import Any, Dict, List, Optional


class HTMLNode:
    """
    Represents an HTML node in a document tree. All fields are optional:
    - tag: the tag name (e.g., "p", "a", "h1"). If None, renders as raw text.
    - value: text value for leaf nodes (assumed when children is None).
    - children: list of child HTMLNode instances (assumed when value is None).
    - props: dict of HTML attributes to render on the tag.
    """

    def __init__(
        self,
        tag: Optional[str] = None,
        value: Optional[str] = None,
        children: Optional[List["HTMLNode"]] = None,
        props: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self) -> str:
        """Render this node to HTML. To be implemented by subclasses."""
        raise NotImplementedError()

    def props_to_html(self) -> str:
        """
        Return a string of HTML attributes with a leading space before each
        attribute. Returns an empty string when there are no props.
        Example: ' href="https://www.google.com" target="_blank"'
        """
        if not self.props:
            return ""
        parts: List[str] = []
        for key, val in self.props.items():
            parts.append(f' {key}="{val}"')
        return "".join(parts)

    def __repr__(self) -> str:
        return (
            f"HTMLNode(tag={self.tag}, value={self.value}, "
            f"children={self.children}, props={self.props})"
        )
