import re
from HomeBase.modules import Module

def lookup(root, path, idx = 0):
  if len(path) <= idx:
    return root
  target = None
  if isinstance(root, Module):
    if path[idx].encode() in root.children:
      target = root.children[path[idx].encode()]
  elif isinstance(root, list):
    position = int(path[idx])
    if len(root) > position:
      target = root[int(path[idx])]
  elif isinstance(root, dict):
    if path[idx] in root:
      target = root[path[idx]]
  else:
    raise Exception("Can't query {}".format(root))
  if target == None:
    raise Exception("Invalid path: {} (@ {} -> {})".format(path, idx, path[idx]))
  if isinstance(target, Module) and target.is_leaf:
    target = target.answer_GET({})

  return lookup(target, path, idx + 1)

def query(root, expression):
  if isinstance(path, str):
    if path[0] == '@':
      return lookup(root, re.split('/', path[1:]), idx)
  raise Exception("Invalid Query: {}".format(expression))
