import re
pattern = re.compile(r'^#([0-9A-Fa-f]{3}$)|(^#[0-9A-Fa-f]{6}$)')
matcher = pattern.match('#aeeeee')
print(matcher.group())