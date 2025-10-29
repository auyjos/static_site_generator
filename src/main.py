import os
import shutil

from inline_markdown import extract_title, markdown_to_html_node


def copy_directory_contents(src, dst):
    """
    Recursively copy all contents from src directory to dst directory.
    
    Args:
        src: Source directory path
        dst: Destination directory path
    """
    # If destination exists, remove it completely
    if os.path.exists(dst):
        print(f"Removing existing directory: {dst}")
        shutil.rmtree(dst)
    
    # Create the destination directory
    print(f"Creating directory: {dst}")
    os.mkdir(dst)
    
    # Recursively copy contents
    _copy_recursive(src, dst)


def _copy_recursive(src, dst):
    """
    Helper function to recursively copy directory contents.
    
    Args:
        src: Source directory path
        dst: Destination directory path
    """
    # List all items in the source directory
    items = os.listdir(src)
    
    for item in items:
        src_path = os.path.join(src, item)
        dst_path = os.path.join(dst, item)
        
        if os.path.isfile(src_path):
            # Copy file
            print(f"Copying file: {src_path} -> {dst_path}")
            shutil.copy(src_path, dst_path)
        else:
            # Create directory and recursively copy its contents
            print(f"Creating directory: {dst_path}")
            os.mkdir(dst_path)
            _copy_recursive(src_path, dst_path)


def generate_page(from_path, template_path, dest_path):
    """
    Generate an HTML page from a markdown file using a template.
    
    Args:
        from_path: Path to the markdown file
        template_path: Path to the HTML template file
        dest_path: Path where the generated HTML should be written
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    # Read the markdown file
    with open(from_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Read the template file
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Convert markdown to HTML
    html_node = markdown_to_html_node(markdown_content)
    html_content = html_node.to_html()
    
    # Extract the title
    title = extract_title(markdown_content)
    
    # Replace placeholders in template
    final_html = template_content.replace("{{ Title }}", title)
    final_html = final_html.replace("{{ Content }}", html_content)
    
    # Ensure the destination directory exists
    dest_dir = os.path.dirname(dest_path)
    if dest_dir and not os.path.exists(dest_dir):
        print(f"Creating directory: {dest_dir}")
        os.makedirs(dest_dir)
    
    # Write the final HTML to the destination file
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    
    print(f"Page generated successfully at {dest_path}")

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    """
    Recursively generate HTML pages from all markdown files in a directory.
    
    Args:
        dir_path_content: Path to the content directory
        template_path: Path to the HTML template file
        dest_dir_path: Path to the destination directory
    """
    items = os.listdir(dir_path_content)

    for item in items:
        src_path = os.path.join(dir_path_content, item)
        dest_path = os.path.join(dest_dir_path, item)

        if os.path.isfile(src_path):
            if src_path.endswith('.md'):
                dest_path = dest_path.replace('.md', '.html')
                generate_page(src_path, template_path, dest_path)
        else:
            generate_pages_recursive(src_path, template_path, dest_path)



def main():
    """
    Main function to generate the static site.
    """
    print("Starting static site generation...")
    
    # Get the project root directory (parent of src directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # Define directories relative to project root
    static_dir = os.path.join(project_root, "static")
    public_dir = os.path.join(project_root, "public")
    content_dir = os.path.join(project_root, "content")
    template_path = os.path.join(project_root, "template.html")
    
    print(f"Project root: {project_root}")
    print(f"Static dir: {static_dir}")
    print(f"Public dir: {public_dir}")
    print(f"Content dir: {content_dir}")
    print(f"Template: {template_path}")
    
    # Copy static files to public directory
    copy_directory_contents(static_dir, public_dir)
    
    generate_pages_recursive(content_dir, template_path, public_dir)
    print("Static site generation complete!")


if __name__ == "__main__":
    main()