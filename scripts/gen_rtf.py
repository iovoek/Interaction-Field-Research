import re

with open('/home/ubuntu/interaction-field-research/exchange_is_the_equation_FULL.md', 'r') as f:
    md = f.read()

rtf = r'{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}' + '\n'
rtf += r'\f0\fs24 ' + '\n'

for line in md.split('\n'):
    if line.startswith('## '):
        rtf += r'\par\b\fs32 ' + line[3:] + r'\b0\fs24\par' + '\n'
    elif line.startswith('### '):
        rtf += r'\par\b\fs28 ' + line[4:] + r'\b0\fs24\par' + '\n'
    elif line.startswith('#### '):
        rtf += r'\par\b\fs26 ' + line[5:] + r'\b0\fs24\par' + '\n'
    elif line.startswith('# '):
        rtf += r'\par\b\fs36 ' + line[2:] + r'\b0\fs24\par' + '\n'
    elif line.startswith('---'):
        rtf += r'\par\line' + '\n'
    elif line.startswith('```'):
        pass
    elif line.startswith('| '):
        rtf += r'\par ' + line + r'\par' + '\n'
    elif line.startswith('> '):
        rtf += r'\par\li720\i ' + line[2:] + r'\i0\li0\par' + '\n'
    elif line.startswith('- '):
        rtf += r'\par\li360\bullet  ' + line[2:] + r'\li0' + '\n'
    elif line.strip():
        cleaned = re.sub(r'\*\*(.+?)\*\*', r'\\b \1\\b0 ', line)
        cleaned = re.sub(r'\*(.+?)\*', r'\\i \1\\i0 ', cleaned)
        rtf += r'\par ' + cleaned + '\n'
    else:
        rtf += r'\par' + '\n'

rtf += '}'

with open('/home/ubuntu/interaction-field-research/exchange_is_the_equation_FULL.rtf', 'w') as f:
    f.write(rtf)
print('RTF generated successfully')
