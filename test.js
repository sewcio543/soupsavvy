function findMatchingElements(root, tagName, attrs, recursive, limit) {
  function matchesAttributes(element, attrs) {
    for (let [key, val] of Object.entries(attrs)) {
      let attrVal = element.getAttribute(key);
      if (
        attrVal === null ||
        (typeof val === "string" && !attrVal.includes(val)) ||
        (val instanceof RegExp && !val.test(attrVal))
      ) {
        return false;
      }
    }
    return true;
  }

  function collectElements(element, recursive) {
    let matches = [];
    let elements = recursive
      ? element.getElementsByTagName(tagName || "*")
      : element.children;

    for (let el of elements) {
      if (
        (!tagName || el.tagName.toLowerCase() === tagName.toLowerCase()) &&
        matchesAttributes(el, attrs)
      ) {
        matches.push(el);
        if (limit && matches.length >= limit) break;
      }
    }
    return matches;
  }
  return collectElements(root, recursive);
}
