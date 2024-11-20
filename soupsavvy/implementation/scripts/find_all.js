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
