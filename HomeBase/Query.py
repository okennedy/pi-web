import re
from HomeBase.modules import Module

def normalize_child(child):
  if isinstance(child, Module) and child.is_leaf:
    return child.answer_GET({})
  else:
    return child


def get_child(root, path_element):
  target = None
  if isinstance(root, Module):
    if path_element.encode() in root.children:
      target = root.children[path_element.encode()]
  elif isinstance(root, list):
    position = int(path_element)
    if len(root) > position:
      target = root[int(path_element)]
  elif isinstance(root, dict):
    if path_element in root:
      target = root[path_element]
  else:
    raise Exception("Can't query {}".format(root))
  if target == None:
    raise Exception("Invalid path: {} in ".format(path_element, root))

  return normalize_child(target)

def get_children(root):
  children = []
  if isinstance(root, Module):
    children = root.children
  elif isinstance(root, list):
    children = root
  elif isinstance(root, dict):
    children = root.items()
  else:
    raise Exception("Can't query {}".format(root))
  return [ normalize_child(child) for child in children ]

def lookup(root, path, idx = 0):
  if isinstance(path, str):
    path = re.split('/', path)
  if len(path) <= idx:
    return root
  target = get_child(root, path[idx])
  return lookup(target, path, idx + 1)

def query(root, expression):
  if isinstance(expression, str):
    expression = re.split('/', expression)
  objects = [root]
  # print("QUERY!")
  for element in expression:
    # print("Query: {}".format(element))
    if element == "":
      pass
    elif element[0] == "@":
      element = re.split("=", element[1:])
      # print("Lookup x[{}] = {}".format(*element))
      objects = [ 
        child 
        for obj in objects 
        for child in get_children(obj) 
        if str(get_child(child, element[0])) == element[1] 
      ]
    elif element == "*":
      objects = [ 
        child 
        for obj in objects 
        for child in get_children(obj) 
      ]
    else:
      objects = [ get_child(obj, element) for obj in objects ]
  return objects