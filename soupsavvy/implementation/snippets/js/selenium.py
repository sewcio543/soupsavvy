"""JavaScript snippets for selenium implementation."""

FILTER_NODES_SCRIPT = """
function findMatchingElements(root, tagName, attrs, recursive) {
  function matchesAttributes(element, attrs) {
    for (let [key, val] of Object.entries(attrs)) {
      let attrVal = element.getAttribute(key);

      if (attrVal === null) {
        return false;
      }

      if (typeof val === "string" && !attrVal.split(" ").includes(val)) {
        return false;
      }
    }
    return true;
  }

  function collectElements(element, recursive) {
    let matches = [];
    let elements = recursive ? element.querySelectorAll("*") : element.children;

    for (let el of elements) {
      if (
        (!tagName || el.tagName.toLowerCase() === tagName.toLowerCase()) &&
        matchesAttributes(el, attrs)
      ) {
        matches.push(el);
      }
    }
    return matches;
  }
  return collectElements(root, recursive);
}

return findMatchingElements(
  arguments[0],
  arguments[1],
  arguments[2],
  arguments[3]
);
"""

FIND_ANCESTORS_SCRIPT = """
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
"""

FIND_PARENT_NODE_SCRIPT = "return arguments[0].parentNode;"
CLICK_ELEMENT_SCRIPT = "arguments[0].click();"
