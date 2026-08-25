// Render model-generated Markdown without trusting embedded HTML or unsafe URLs.
// Marked remains responsible for formatting; this renderer restricts the parts
// that could otherwise inject active content into the dashboard.
(() => {
  "use strict";

  function escapeMarkdownHtml(value) {
    return String(value ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function safeMarkdownUrl(value) {
    try {
      const parsed = new URL(String(value || ""));
      return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : "";
    } catch (_) {
      return "";
    }
  }

  const renderer = new marked.Renderer();

  renderer.html = ({ text }) => escapeMarkdownHtml(text);

  renderer.link = function ({ href, title, tokens }) {
    const label = this.parser.parseInline(tokens);
    const safeHref = safeMarkdownUrl(href);
    if (!safeHref) return label;

    const safeTitle = title ? ` title="${escapeMarkdownHtml(title)}"` : "";
    return `<a href="${escapeMarkdownHtml(safeHref)}"${safeTitle} target="_blank" rel="noopener noreferrer">${label}</a>`;
  };

  // Remote images are intentionally reduced to their alt text. This prevents
  // model output from loading tracking pixels or untrusted external resources.
  renderer.image = ({ text }) => escapeMarkdownHtml(text);

  globalThis.renderSafeMarkdown = (value) => marked.parse(String(value || ""), { renderer });
})();
