from rich.tree import Tree
from rich import print
import os

def add_items(path, tree):
    for item in sorted(os.listdir(path)):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path):
            branch = tree.add(f"[bold blue]{item}[/]")
            add_items(item_path, branch)
        else:
            tree.add(item)

if __name__ == '__main__':
    project_path = "."  # Change this if needed to your project's root path
    tree = Tree(f"[bold green]Project Root ({os.path.abspath(project_path)})[/bold green]")
    add_items(project_path, tree)
    print(tree)
