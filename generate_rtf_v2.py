"""
Generate an RTF document from the markdown source.
RTF is plain text with control words, so we build it directly.
"""
import re

with open("exchange_is_the_equation_V2.md", "r") as f:
    md = f.read()

def escape_rtf(text):
    text = text.replace("\\", "\\\\")
    text = text.replace("{", "\\{")
    text = text.replace("}", "\\}")
    # Unicode chars
    result = []
    for ch in text:
        if ord(ch) > 127:
            result.append(f"\\u{ord(ch)}?")
        else:
            result.append(ch)
    return "".join(result)

def process_inline(text):
    # Bold **text**
    text = re.sub(r'\*\*(.+?)\*\*', lambda m: '{\\\\b ' + escape_rtf(m.group(1)) + '}', text)
    # Italic *text* or _text_
    text = re.sub(r'\*(.+?)\*', lambda m: '{\\\\i ' + escape_rtf(m.group(1)) + '}', text)
    text = re.sub(r'_(.+?)_', lambda m: '{\\\\i ' + escape_rtf(m.group(1)) + '}', text)
    # Code `text`
    text = re.sub(r'`(.+?)`', lambda m: '{\\\\f1 ' + escape_rtf(m.group(1)) + '}', text)
    return text

lines = md.split("\n")
rtf_body = []

i = 0
while i < len(lines):
    line = lines[i]

    # Heading 1
    if line.startswith("# ") and not line.startswith("## "):
        text = escape_rtf(line[2:].strip())
        rtf_body.append(f"\\pard\\sb360\\sa120\\b\\fs36 {text}\\b0\\par")

    # Heading 2
    elif line.startswith("## ") and not line.startswith("### "):
        text = escape_rtf(line[3:].strip())
        rtf_body.append(f"\\pard\\sb300\\sa100\\b\\fs28 {text}\\b0\\par")

    # Heading 3
    elif line.startswith("### "):
        text = escape_rtf(line[4:].strip())
        rtf_body.append(f"\\pard\\sb240\\sa80\\b\\fs24 {text}\\b0\\par")

    # Heading 4
    elif line.startswith("#### "):
        text = escape_rtf(line[5:].strip())
        rtf_body.append(f"\\pard\\sb200\\sa60\\b\\fs22 {text}\\b0\\par")

    # Horizontal rule
    elif line.strip() in ("---", "***", "___"):
        rtf_body.append("\\pard\\sb120\\sa120\\brdrb\\brdrs\\brdrw10\\brsp20 \\par")

    # Blockquote
    elif line.startswith("> "):
        text = process_inline(line[2:].strip())
        rtf_body.append(f"\\pard\\li720\\ri720\\sb120\\sa120\\i {text}\\i0\\par")

    # Code block (```)
    elif line.startswith("```"):
        i += 1
        code_lines = []
        while i < len(lines) and not lines[i].startswith("```"):
            code_lines.append(escape_rtf(lines[i]))
            i += 1
        code_text = "\\line ".join(code_lines)
        rtf_body.append(f"\\pard\\li360\\ri360\\sb120\\sa120\\f1\\fs18 {code_text}\\f0\\fs22\\par")

    # Bullet list
    elif line.startswith("- ") or line.startswith("* "):
        text = process_inline(escape_rtf(line[2:].strip()))
        rtf_body.append(f"\\pard\\li360\\fi-180\\sb60\\sa60 \\bullet  {text}\\par")

    # Numbered list
    elif re.match(r'^\d+\. ', line):
        text = process_inline(escape_rtf(re.sub(r'^\d+\. ', '', line).strip()))
        num = re.match(r'^(\d+)\.', line).group(1)
        rtf_body.append(f"\\pard\\li360\\fi-180\\sb60\\sa60 {num}.  {text}\\par")

    # Empty line
    elif line.strip() == "":
        rtf_body.append("\\pard\\sb60\\sa60 \\par")

    # Normal paragraph
    else:
        text = process_inline(escape_rtf(line.strip()))
        if text:
            rtf_body.append(f"\\pard\\sb120\\sa120\\fs22 {text}\\par")

    i += 1

rtf_header = r"""{\rtf1\ansi\deff0
{\fonttbl
{\f0\froman\fcharset0 Georgia;}
{\f1\fmodern\fcharset0 Courier New;}
}
{\colortbl;\red0\green0\blue0;\red201\green168\blue76;\red42\green157\blue143;}
\paperw12240\paperh15840
\margl1440\margr1440\margt1440\margb1440
\widowctrl\hyphauto
\fs22\f0
"""

rtf_footer = "\n}"

rtf_content = rtf_header + "\n".join(rtf_body) + rtf_footer

with open("exchange_is_the_equation_V2.rtf", "w", encoding="ascii", errors="replace") as f:
    f.write(rtf_content)

print("RTF generated successfully.")
