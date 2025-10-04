"""JavaScript snippets for playwright implementation."""

FIND_ANCESTORS_SCRIPT = """
(element, limit) => {
  function findAncestors(el, lim) {
    const ancestors = [];
    let parent = el.parentElement;
    while (parent && parent.nodeType === 1) {
      ancestors.push(parent);
      if (lim && ancestors.length >= lim) break;
      parent = parent.parentElement;
    }
    return ancestors;
  }
  return findAncestors(element, limit);
}
"""

FILTER_NODES_SCRIPT = """
(element, args) => {
  const [tagName, attrs, recursive] = args;

  function matchesAttributes(element, attrs) {
    for (const [key, val] of Object.entries(attrs)) {
      const attrVal = element.getAttribute(key);
      if (attrVal === null) return false;

      if (typeof val === "string" && !attrVal.split(" ").includes(val)) {
        return false;
      }
    }
    return true;
  }

  function collectElements(element, recursive) {
    const matches = [];
    const elements = recursive ? element.querySelectorAll("*") : element.children;

    for (const el of elements) {
      if (
        (!tagName || el.tagName.toLowerCase() === tagName.toLowerCase()) &&
        matchesAttributes(el, attrs)
      ) {
        matches.push(el);
      }
    }

    return matches;
  }

  return collectElements(element, recursive);
}
"""

ADD_IDENTIFIER_SCRIPT = """
el => {
    if (!el._uid) {
        el._uid = Math.random().toString(36).substr(2, 9);
    }
    return el._uid;
}
"""

PARENT_ELEMENT_SCRIPT = "el => el.parentElement"
TAG_NAME_SCRIPT = "el => el.tagName"
OUTER_HTML_SCRIPT = "el => el.outerHTML"
CLICK_ELEMENT_SCRIPT = "el => el.click()"
GET_ATTRIBUTE_SCRIPT = "(el, name) => el[name]"
