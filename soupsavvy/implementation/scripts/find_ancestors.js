function findAncestors(element, limit) {
  let ancestors = [];
  let parent = element.parentNode;
  while (parent && parent.nodeType === 1) {
    ancestors.push(parent);
    if (limit && ancestors.length >= limit) break;
    parent = parent.parentNode;
  }
  return ancestors;
}
return findAncestors(arguments[0], arguments[1]);
