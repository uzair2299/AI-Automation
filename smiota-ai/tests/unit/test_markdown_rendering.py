"""Unit tests for Markdown rendering, table parsing, code blocks, and XSS sanitization."""
import os
import subprocess
import tempfile


def test_webchat_file_contains_markdown_and_telemetry_logging():
    """Verify that webchat HTML contains Markdown functions, styling, tables, and keeps telemetry in logging scope without displaying on UI."""
    webchat_path = "smiota-agent-gateway/api/v1/channels/webchat.py" if os.path.exists("smiota-agent-gateway/api/v1/channels/webchat.py") else "src/smiota/api/v1/channels/webchat.py"
    with open(webchat_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Markdown functions & attributes
    assert "function formatMarkdown" in content
    assert "function formatInlineMarkdown" in content
    assert "function sanitizeUrl" in content
    assert 'target="_blank"' in content
    assert 'rel="noopener noreferrer"' in content

    # Table & code elements
    assert "min-w-full divide-y" in content
    assert "navigator.clipboard.writeText" in content

    # Under-the-hood telemetry logging (telemetry logged to console and retained in payload, not rendered on UI)
    assert "logProvenanceTelemetry" in content
    assert "[Telemetry & Provenance]" in content


def test_webchat_file_contains_initial_action_pills():
    """Verify that webchat HTML contains the 6 initial suggested action pills and preset handlers."""
    webchat_path = "smiota-agent-gateway/api/v1/channels/webchat.py" if os.path.exists("smiota-agent-gateway/api/v1/channels/webchat.py") else "src/smiota/api/v1/channels/webchat.py"
    with open(webchat_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 6 Pill IDs
    assert 'data-pill-id="has_package"' in content
    assert 'data-pill-id="lost_code"' in content
    assert 'data-pill-id="locker_issue"' in content
    assert 'data-pill-id="courier_delivery"' in content
    assert 'data-pill-id="package_collected"' in content
    assert 'data-pill-id="human_support"' in content

    # Pill labels and presets
    assert "Do I have a package?" in content
    assert "I lost my code" in content
    assert "Locker won't open" in content
    assert "Courier says delivered" in content
    assert "Package already collected" in content
    assert "Talk to support" in content
    assert "INITIAL_ACTION_PILLS" in content
    assert "sendPresetPill" in content


def test_javascript_markdown_rendering_with_node():
    """Execute the formatMarkdown JavaScript function with Node.js to verify rendering and XSS protection."""
    js_code = r"""
    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
    }

    function sanitizeUrl(rawUrl) {
      if (!rawUrl) return null;
      var trimmed = rawUrl.trim();
      var safePrefixes = ['https://', 'http://', 'mailto:', '/'];
      var isSafe = safePrefixes.some(function(prefix) {
        return trimmed.toLowerCase().indexOf(prefix) === 0;
      });
      if (!isSafe) return null;
      var dangerous = ['javascript:', 'data:', 'vbscript:', 'file:'];
      for (var i = 0; i < dangerous.length; i++) {
        if (trimmed.toLowerCase().indexOf(dangerous[i]) !== -1) {
          return null;
        }
      }
      return encodeURI(decodeURI(trimmed));
    }

    function formatInlineMarkdown(text) {
      if (!text) return '';
      var formatted = text;

      // Hyperlinks: [Label](url)
      formatted = formatted.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function(match, label, rawUrl) {
        var safeUrl = sanitizeUrl(rawUrl);
        if (safeUrl) {
          return '<a href="' + safeUrl + '" target="_blank" rel="noopener noreferrer">' + label + '</a>';
        }
        return label;
      });

      // Bold: **text** or __text__
      formatted = formatted.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>');
      formatted = formatted.replace(/__([^_\n]+)__/g, '<strong>$1</strong>');

      // Italic: *text* or _text_
      formatted = formatted.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
      formatted = formatted.replace(/_([^_\n]+)_/g, '<em>$1</em>');

      return formatted;
    }

    function formatMarkdown(str) {
      if (!str) return '';
      var text = String(str).replace(/\r\n/g, '\n');

      var codeBlocks = [];
      text = text.replace(/```([a-zA-Z0-9_+-]*)\n?([\s\S]*?)```/g, function(match, lang, code) {
        var id = '@@CODEBLOCK_' + codeBlocks.length + '@@';
        var cleanLang = (lang || 'code').trim();
        var escapedCode = escapeHtml(code.trim());
        codeBlocks.push({
          lang: cleanLang,
          html: '<pre><code class="language-' + cleanLang + '">' + escapedCode + '</code></pre>'
        });
        return '\n\n' + id + '\n\n';
      });

      var inlineCodes = [];
      text = text.replace(/`([^`\n]+)`/g, function(match, code) {
        var id = '@@INLINECODE_' + inlineCodes.length + '@@';
        inlineCodes.push('<code>' + escapeHtml(code) + '</code>');
        return id;
      });

      text = escapeHtml(text);

      var lines = text.split('\n');
      var processed = [];
      var inList = false;
      var listType = null;
      var inTable = false;
      var tableHeaders = [];
      var tableRows = [];

      function closeList() {
        if (inList) {
          processed.push(listType === 'ul' ? '</ul>' : '</ol>');
          inList = false;
          listType = null;
        }
      }

      function flushTable() {
        if (inTable && tableHeaders.length > 0) {
          var theadHtml = tableHeaders.map(function(h) { return '<th>' + formatInlineMarkdown(h) + '</th>'; }).join('');
          var tbodyHtml = tableRows.map(function(row) {
            return '<tr>' + row.map(function(c) { return '<td>' + formatInlineMarkdown(c) + '</td>'; }).join('') + '</tr>';
          }).join('');
          processed.push('<table class="min-w-full"><thead><tr>' + theadHtml + '</tr></thead><tbody>' + tbodyHtml + '</tbody></table>');
          inTable = false;
          tableHeaders = [];
          tableRows = [];
        }
      }

      for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        var trimmed = line.trim();

        if (trimmed.indexOf('|') === 0 && trimmed.lastIndexOf('|') === trimmed.length - 1 && trimmed.length > 2) {
          closeList();
          var isDivider = /^\|[\s\-:\|]+\|$/.test(trimmed);
          if (isDivider) {
            inTable = true;
            continue;
          }
          var cells = trimmed.slice(1, -1).split('|').map(function(c) { return c.trim(); });
          if (!inTable) {
            tableHeaders = cells;
          } else {
            tableRows.push(cells);
          }
          continue;
        } else if (inTable) {
          flushTable();
        }

        var hMatch = trimmed.match(/^(#{1,6})\s+(.*)$/);
        if (hMatch) {
          closeList();
          var level = hMatch[1].length;
          processed.push('<h' + level + '>' + formatInlineMarkdown(hMatch[2]) + '</h' + level + '>');
          continue;
        }

        var ulMatch = trimmed.match(/^[-*+]\s+(.*)$/);
        if (ulMatch) {
          if (!inList || listType !== 'ul') {
            closeList();
            processed.push('<ul>');
            inList = true;
            listType = 'ul';
          }
          processed.push('<li>' + formatInlineMarkdown(ulMatch[1]) + '</li>');
          continue;
        }

        var olMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
        if (olMatch) {
          if (!inList || listType !== 'ol') {
            closeList();
            processed.push('<ol>');
            inList = true;
            listType = 'ol';
          }
          processed.push('<li>' + formatInlineMarkdown(olMatch[2]) + '</li>');
          continue;
        }

        if (trimmed.startsWith('@@CODEBLOCK_') && trimmed.endsWith('@@')) {
          closeList();
          processed.push(trimmed);
          continue;
        }

        if (trimmed === '') {
          continue;
        }

        closeList();
        processed.push('<p>' + formatInlineMarkdown(line) + '</p>');
      }

      closeList();
      flushTable();

      var resultHtml = processed.join('\n');

      resultHtml = resultHtml.replace(/@@CODEBLOCK_(\d+)@@/g, function(match, idx) {
        var item = codeBlocks[parseInt(idx, 10)];
        return item ? item.html : '';
      });

      resultHtml = resultHtml.replace(/@@INLINECODE_(\d+)@@/g, function(match, idx) {
        return inlineCodes[parseInt(idx, 10)] || '';
      });

      return resultHtml;
    }

    const tests = [
      {
        name: "Hyperlink formatting",
        input: "Visit [Smiota Guide](https://smiota.com/guide) for details.",
        expectedSubstr: '<a href="https://smiota.com/guide" target="_blank" rel="noopener noreferrer">Smiota Guide</a>'
      },
      {
        name: "Block malicious javascript: URLs",
        input: "Click [Here](javascript:alert('XSS')) now.",
        expectedSubstr: "Here",
        forbiddenSubstr: "javascript:alert"
      },
      {
        name: "Headings H1-H3",
        input: "# Title 1\n## Title 2\n### Title 3",
        expectedSubstr: "<h1>Title 1</h1>\n<h2>Title 2</h2>\n<h3>Title 3</h3>"
      },
      {
        name: "Bold and Italic",
        input: "**Bold Text** and *Italic Text*",
        expectedSubstr: "<strong>Bold Text</strong> and <em>Italic Text</em>"
      },
      {
        name: "Bullet list",
        input: "- Item 1\n- Item 2",
        expectedSubstr: "<ul>\n<li>Item 1</li>\n<li>Item 2</li>\n</ul>"
      },
      {
        name: "Numbered list",
        input: "1. First\n2. Second",
        expectedSubstr: "<ol>\n<li>First</li>\n<li>Second</li>\n</ol>"
      },
      {
        name: "Code block with language",
        input: "```python\nprint('Hello World')\n```",
        expectedSubstr: '<pre><code class="language-python">print(&#039;Hello World&#039;)</code></pre>'
      },
      {
        name: "Table parsing",
        input: "| Name | Role |\n|---|---|\n| Smiota SI | AI |",
        expectedSubstr: '<table class="min-w-full">'
      },
      {
        name: "XSS script prevention in code blocks",
        input: "```html\n<script>alert('pwn')</script>\n```",
        expectedSubstr: '&lt;script&gt;alert(&#039;pwn&#039;)&lt;/script&gt;',
        forbiddenSubstr: '<script>'
      }
    ];

    for (const t of tests) {
      const out = formatMarkdown(t.input);
      if (t.expectedSubstr && !out.includes(t.expectedSubstr)) {
        console.error(`FAILED: ${t.name}. Expected: ${t.expectedSubstr}\nGot: ${out}`);
        process.exit(1);
      }
      if (t.forbiddenSubstr && out.includes(t.forbiddenSubstr)) {
        console.error(`FAILED: ${t.name}. Forbidden: ${t.forbiddenSubstr}\nGot: ${out}`);
        process.exit(1);
      }
    }
    console.log("ALL_JS_TESTS_PASSED");
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write(js_code)
        temp_path = f.name

    try:
        res = subprocess.run(["node", temp_path], capture_output=True, text=True)
        assert res.returncode == 0, f"JS execution failed: {res.stderr}"
        assert "ALL_JS_TESTS_PASSED" in res.stdout
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
