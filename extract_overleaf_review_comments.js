(() => {
  const normalize = (value) =>
    String(value || "")
      .replace(/\u00a0/g, " ")
      .replace(/\s+/g, " ")
      .trim();

  const buttons = Array.from(document.querySelectorAll("button"));

  for (const button of buttons) {
    const text = normalize(button.innerText || button.textContent || button.getAttribute("aria-label"));
    if (/show more/i.test(text)) {
      button.click();
    }
  }

  const rawBlocks = Array.from(document.querySelectorAll("button, [role='button'], li, div"))
    .map((element) => {
      const text = normalize(element.innerText || element.textContent || element.getAttribute("aria-label"));
      return {
        tag: element.tagName,
        className: normalize(element.className),
        text,
      };
    })
    .filter((item) =>
      item.text.includes("tkc004") &&
      item.text.includes("Reply") &&
      (item.text.includes("Resolve comment") || item.text.includes("More options"))
    )
    .filter((item) => item.text.length > 40 && item.text.length < 3000)
    .map((item) => item.text);

  const unique = [];
  for (const text of rawBlocks) {
    if (!unique.includes(text)) {
      unique.push(text);
    }
  }

  const minimal = unique.filter((text) => {
    const longerContainers = unique.filter((other) => other !== text && other.includes(text));
    return longerContainers.length === 0 || text.split("Resolve comment").length > 2;
  });

  const comments = minimal.map((raw, index) => {
    const cleaned = raw
      .replace(/\bResolve comment\b/g, "")
      .replace(/\bMore options\b/g, "")
      .replace(/\bReply\b/g, "")
      .replace(/\bshow more\b/gi, "")
      .replace(/\s+\.\.\./g, " ...")
      .replace(/\s+/g, " ")
      .trim();

    return {
      index: index + 1,
      raw,
      cleaned,
    };
  });

  return JSON.stringify(
    {
      exportedAt: new Date().toISOString(),
      source: "Chrome active tab DOM",
      url: location.href,
      title: document.title,
      count: comments.length,
      comments,
    },
    null,
    2
  );
})();
