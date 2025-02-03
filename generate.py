#! /usr/bin/python3

import os
import sys

class Section:
	def __init__(self, idn, title, level = 1):
		self.idn = idn
		self.title = title
		self.level = level
		self.content = []

class Reference:
	def __init__(self, idn, url, title = None):
		self.idn = idn
		self.title = title
		self.url = url
		self.number = 0

class Itemrow:
	def __init__(self, *parts):
		self.parts = parts
		self.subtable = []

class Row:
	def __init__(self, offset, _type, comment):
		self.offset = offset
		self.type = _type
		self.comment = comment
		self.subtable = []

class Subrow:
	def __init__(self, bits, comment):
		self.bits = bits
		self.comment = comment
		self.subtable = []

class Optionrow:
	def __init__(self, value, comment):
		self.value = value
		self.comment = comment
		self.subtable = []

def count_start(text, c):
	for i, c1 in enumerate(text):
		if c != c1:
			return i
	return len(text)

def make_ref(idn):
	if type(idn) is int:
		return f"node{idn}"
	else:
		assert idn != ""
		return idn

class Document:
	def __init__(self, idn, title):
		self.idn = idn
		self.title = title
		self.sections = []
		self.references = []
		self.by_name = {}

	def convert_text(self, text):
		if text is None:
			return ""

		result = ""
		while '{' in text:
			ix = text.find('{')
			ix2 = text.find('}', ix)
			ref = text[ix + 1:ix2]
			if '|' in ref:
				ix3 = ref.find('|')
				url = ref[:ix3]
				content = ref[ix3 + 1:]
				subst = f"<a href=\"{url}\" target=\"_blank\">{content}</a>"
			else:
				entity = self.by_name.get(ref)
				if type(entity) is Section:
					subst = f"<a href=\"#{self.idn}_{make_ref(entity.idn)}\">{entity.title}</a>"
				elif type(entity) is Reference:
					assert type(entity.idn) is str and entity.idn != ""
					subst = f"<a href=\"#{self.idn}_{entity.idn}\"><sup title=\"{entity.title}\">[{entity.number}]</sup></a>"
				else:
					subst = f"<u title=\"{ref}\">???</u>"
			result += text[:ix] + subst
			text = text[ix2 + 1:]
		text = result + text

		# replace hexadecimals
		result = ""
		while '0x' in text:
			ix = text.find('0x')
			start_tt = result.rfind('<tt')
			stop_tt = result.rfind('</tt>')
			if ix == 0 or not text[ix - 1].isalnum() and (start_tt == -1 or start_tt < stop_tt):
				result += text[:ix] + "<tt><sub>x</sub>"
				ix2 = ix + 2
				while ix2 < len(text) and ('0' <= text[ix2] <= '9' or 'A' <= text[ix2].upper() <= 'F'):
					result += text[ix2]
					ix2 += 1
				result += "</tt>"
				text = text[ix2:]
			else:
				result += text[:ix + 2]
				text = text[ix + 2:]

		result = result + text
		return result.replace('<=', '&le;').replace('>=', '&ge;')

entries = []
stack = []

"""
fmt>
	year
	title
	title_comment
	title_target
	ext*
	magic*
	arch
	inf
	ignore_toc_entries

	sys*
		sys_date_earliest
		sys_date_latest
		sys_date
		sys_before
		sys_until
		sys_target
"""

DESCRIPTIONS = False

CURRENT_DOCUMENT = None
DOCUMENTS = {}

filename = os.path.splitext(sys.argv[0])[0] + '.dat' if len(sys.argv) < 2 else sys.argv[1]
basename = os.path.splitext(sys.argv[0] if len(sys.argv) < 2 else sys.argv[1])[0]
node_counter = 0

with open(filename, 'r') as file:
	for line in file:
		if not DESCRIPTIONS:
			line = line.strip()
			if len(line) == 0 or line.startswith('#'):
				continue
			if line == 'DESCRIPTIONS':
				DESCRIPTIONS = True
				continue
			assert line[0] == '.'
			ix = line.find(':')
			assert ix != -1
			tag = line[1:ix]
			value = line[ix + 1:]
			ix = tag.find('/')
			if ix != -1:
				level = int(tag[ix + 1:])
				tag = tag[:ix]
			else:
				level = 1
			#print(tag, level, value, file = sys.stderr)
			if tag in 'fmt':
				entry = {'.type': 'fmt', 'fmt': value, '.level': level}
				while len(stack) > 0 and stack[-1]['.type'] != 'fmt':
					stack.pop()
				while len(stack) > 0 and stack[-1]['.level'] >= level:
					stack.pop()
				if level == 1:
					entries.append(entry)
				else:
					if '.fmt' not in stack[-1]:
						stack[-1]['.fmt'] = []
					stack[-1]['.fmt'].append(entry)
				stack.append(entry)
			elif tag == 'sys':
				assert level == 1
				if stack[-1]['.type'] == 'sys':
					stack.pop()
				if 'sys' not in stack[-1]:
					stack[-1]['sys'] = []
				entry = {'.type': 'sys', 'sys': value}
				stack[-1]['sys'].append(entry)
				stack.append(entry)
			elif tag in {'title', 'title_comment', 'title_target', 'ext', 'magic', 'arch', 'inf', 'ignore_toc_entries'}:
				assert level == 1
				if tag == 'title':
					while stack[-1]['.type'] not in {'fmt'}:
						stack.pop()
				else:
					while stack[-1]['.type'] != 'fmt':
						stack.pop()
				if tag in {'ext', 'magic'}:
					if tag not in stack[-1]:
						stack[-1][tag] = []
					stack[-1][tag].append(value)
				else:
					stack[-1][tag] = value
			elif tag in {'sys_date_earliest', 'sys_date_latest', 'sys_date', 'sys_before', 'sys_until', 'sys_target'}:
				assert level == 1
				assert stack[-1]['.type'] == 'sys'
				stack[-1][tag] = value
			else:
				assert False

		else:
			if line.strip().startswith("#") or line.strip() == '':
				continue
			elif line.startswith("TITLE "):
				data = line[len("TITLE "):].strip()
				ix = data.find(':')
				idn = data[:ix].strip()
				assert idn != ""
				title = data[ix + 1:].strip()
				CURRENT_DOCUMENT = Document(idn, title)
				DOCUMENTS[idn] = CURRENT_DOCUMENT
			elif line.startswith("SECTION "):
				#if CURRENT_DOCUMENT is None:
				#	CURRENT_DOCUMENT = Document(None, basename)
				#	DOCUMENTS[''] = CURRENT_DOCUMENT
				data = line[len("SECTION "):]
				ix0 = data.find('/')
				ix = data.find(':')
				if ix0 != -1 and ix0 < ix:
					level = int(data[:ix0].strip()) + 1
					data = data[ix0 + 1:]
					ix -= ix0 + 1
				else:
					level = 1
				idn = data[:ix].strip()
				if idn == "":
					idn = node_counter
					node_counter += 1
				title = data[ix + 1:].strip()
				section = Section(idn, title, level)
				CURRENT_DOCUMENT.sections.append(section)
				if type(idn) is str:
					assert idn not in CURRENT_DOCUMENT.by_name
					CURRENT_DOCUMENT.by_name[idn] = section
			elif line.startswith(">"):
				#if len(DOCUMENTS) == 0:
				#	DOCUMENTS.append(Document(None, basename))
				data = line[1:].strip()
				if len(CURRENT_DOCUMENT.sections) > 0:
					CURRENT_DOCUMENT.sections[-1].content.append(data)
			elif line.startswith("REFERENCE "):
				#if len(DOCUMENTS) == 0:
				#	DOCUMENTS.append(Document(None, basename))
				data = line[len("REFERENCE "):].strip()
				assert data[0] == '{'
				ix = data.find('}')
				idn = data[1:ix]
				if idn == "":
					idn = node_counter
					node_counter += 1
				data = data[ix + 1:].strip()
				if data[0] == '"':
					ix = data.find('"', 1)
					title = data[1:ix]
					url = data[ix + 1:].strip()
					if url == "":
						url = None
				else:
					title = data
					url = data
				reference = Reference(idn, url, title)
				CURRENT_DOCUMENT.references.append(reference)
				reference.number = len(CURRENT_DOCUMENT.references)
				CURRENT_DOCUMENT.by_name[idn] = reference
			else:
				#if len(DOCUMENTS) == 0:
				#	DOCUMENTS.append(Document(None, basename))
				indent = count_start(line, '\t')
				parts = line.strip().split('\t')
				if indent == 0:
					selector = None
				else:
					assert indent >= 2
					current = CURRENT_DOCUMENT.sections[-1].content
					for i in range(1, indent):
						current = current[-1].subtable
				selector = parts.pop(0)

				if selector.startswith('@'):
					# field at specified offset
					offset = selector[1:]
					if '/' in offset:
						offset = tuple(offset.split('/'))
					if len(parts) == 0:
						_type = None
					else:
						_type = parts.pop(0)
						if '/' in _type:
							_type = tuple(_type.split('/'))
					if len(parts) == 0:
						comment = None
					else:
						comment = '\t'.join(parts)
					row = Row(offset, _type, comment)
				elif selector.startswith('%'):
					# bitfield
					if len(parts) == 0:
						comment = None
					else:
						comment = '\t'.join(parts)
					row = Subrow(selector[1:], comment)
				elif selector.startswith('='):
					# option value
					if len(parts) == 0:
						comment = None
					else:
						comment = '\t'.join(parts)
					row = Optionrow(selector[1:], comment)
				else:
					row = Itemrow(selector, *parts)

				if indent == 0:
					if len(CURRENT_DOCUMENT.sections) > 0:
						CURRENT_DOCUMENT.sections[-1].content.append(row)
				else:
					current.append(row)

for entry in entries:
	members = [entry]
	while len(members) > 0:
		member = members.pop(0)
		if '.fmt' in member:
			members = member['.fmt'] + members
		earliest_date = None
		for system in member.get('sys', []):
			if 'sys_date' in system:
				current_date = system['sys_date']
			elif 'sys_date_latest' in system:
				# we are interested in the latest possible date it could have appeared, everything else is speculation
				current_date = system['sys_date_latest']
			else:
				continue
			ix = current_date.find('-')
			if ix != -1:
				current_date = current_date[:ix]
			if current_date.lower().startswith('around '):
				current_date = current_date[7:]
			try:
				current_date = int(current_date)
			except ValueError:
				continue # can't process non-integer
			if earliest_date is None or current_date < earliest_date:
				earliest_date = current_date
		if earliest_date is not None:
			member['year'] = str(earliest_date)

#print(entries)

#SPLITHTML = True
SPLITHTML = False
#CREATEDIR = True
CREATEDIR = False

def make_hex(text):
	if len(text) > 0 and ('0' <= text[0] <= '9' or 'A' <= text[0].upper() <= 'F'):
		return '<sub>x</sub>' + text
	else:
		return text

def print_row(document, row, option_count = 1, file = None):
	if type(row) is Itemrow:
		print("<tr>\n<td>" + "</td>\n<td>".join(map(document.convert_text, row.parts)), end = "", file = file)
	elif type(row) is Row:
		if option_count > 1:
			colspan = f" colspan='{option_count}'"
		else:
			colspan = ""
		if type(row.offset) is tuple:
			#assert option_count == row.offset
			#offset = tuple(map(make_hex, row.offset))
			#offset = "<td><tt>" + "</tt></td><td><tt>".join(offset) + "</tt></td>"
			offset = ''.join("<td><tt>" + make_hex(entry) + "</tt></td>" if entry != '-' else "<td style='background:gray;'>&nbsp;&nbsp;&nbsp;</td>" for entry in row.offset)
		else:
			offset = make_hex(row.offset)
			offset = f"<td{colspan}><tt>{offset}</tt></td>"
		if type(row.type) is tuple:
			#assert option_count == row.offset
			#row_type = "<td>" + "</td><td>".join(row.type) + "</td>"
			row_type = ''.join("<td>" + entry + "</td>" if entry != '-' else "<td style='background:gray;'>&nbsp;&nbsp;&nbsp;</td>" for entry in row.type)
		else:
			row_type = f"<td{colspan}>{row.type}</td>"
		print(f"<tr>\n{offset}\t{row_type}\n<td>{document.convert_text(row.comment)}", end = "", file = file)
	elif type(row) is Subrow:
		bits = "Bits" if ':' in row.bits else "Bit"
		print(f"<tr>\n<td>{bits} {row.bits}</td>\n<td>{document.convert_text(row.comment)}", end = "", file = file)
	elif type(row) is Optionrow:
		print(f"<tr>\n<td>{row.value}</td>\n<td>{document.convert_text(row.comment)}", end = "", file = file)
	if len(row.subtable) > 0:
		print("\n<table border='1'>", file = file)
		#option_count = 1
		#for subrow in row.subtable:
		#	if type(subrow) is Row:
		#		if type(subrow.offset) is tuple:
		#			assert option_count in {1, len(subrow.offset)}
		#			option_count = len(subrow.offset)
		#		if type(subrow.type) is tuple:
		#			assert option_count in {1, len(subrow.type)}
		#			option_count = len(subrow.type)
		for subrow in row.subtable:
			print_row(document, subrow, file = file)
		print("</table>", file = file)
	print("</td></tr>", file = file)

if CREATEDIR:
	if not os.path.isdir(basename):
		os.mkdir(basename)

def get_main_file(basename):
	if CREATEDIR:
		return os.path.join(basename, "index.html")
	else:
		return basename + ".html"

def get_sub_file(basename, subname, nosubdir = False):
	if CREATEDIR:
		if nosubdir:
			return f"{subname}.html"
		else:
			return os.path.join(basename, f"{subname}.html")
	else:
		return f"{basename}.{subname}.html"

file = open(get_main_file(basename), 'w')
print(f"<!-- This file is automatically generated from {filename} -->", file = file)
print("""<html>
<head>
<title>Old computer executable file formats</title>
</head>
<body>

<h1>Table of contents</h1>

<ul>""", file = file)

#PAGE_FEED_CONDITION = lambda member: member.get('.level', 1) == 1
PAGE_FEED_CONDITION = lambda member: True # TODO: this creates orphaned empty children, also AppleSingle/AppleDouble becomes unreachable

current_format = None
for entry in entries:
	members = [entry]
	while len(members) > 0:
		member = members.pop(0)
		if PAGE_FEED_CONDITION(member):
			current_format = get_sub_file(basename, member['fmt'], nosubdir = True)
		if len(member.get('.fmt', [])) == 0 or member.get('ignore_toc_entries') == 'yes':
			if SPLITHTML:
				if PAGE_FEED_CONDITION(member):
					href = f"href=\"{current_format}\" target=\"_blank\""
				else:
					href = f"href=\"{current_format}#{member['fmt']}\" target=\"_bank\""
			else:
				href = f"href=\"#{member['fmt']}\""
			print(f"<li>{member.get('year', '?')} &mdash; <a {href}>{member['title']}</a>{' ' + member['title_comment'] if 'title_comment' in member else ''}{' for ' + member['title_target'] if 'title_target' in member else ''}</li>", file = file)
		else:
			members = member['.fmt'] + members
			if SPLITHTML:
				current_format = get_sub_file(basename, member['fmt'])
print("</ul>", file = file)

for entry in entries:
	members = [entry]
	ignore_toc_entries = False # TODO: this only allows one level of combination
	while len(members) > 0:
		member = members.pop(0)
		if '.fmt' in member:
			members = member['.fmt'] + members
		fmt = member['fmt']
		if SPLITHTML and PAGE_FEED_CONDITION(member) and not ignore_toc_entries:
			print("""</body>
</html>""", file = file)
			file.close()
			file = open(get_sub_file(basename, member['fmt']), "w")
			print(f"""<!-- This file is automatically generated from {filename} -->
<html>
<head>
<title>{member['title']}{' ' + member['title_comment'] if 'title_comment' in member else ''}</title>
</head>
<body>""", file = file)
		else:
			print("<hr/>", file = file)
		if entry.get('ignore_toc_entries') == 'yes':
			ignore_toc_entries = True
		print(f"<h{member['.level']} id=\"{member['fmt']}\">{member['title']}{' ' + member['title_comment'] if 'title_comment' in member else ''}</h{member['.level']}>", file = file)
		if '.fmt' in member and member.get('ignore_toc_entries') != 'yes':
			continue
		print("<dl>\n<dt>File extensions</td>", file = file)
		if len(member.get('ext', [])) == 0:
			print("<dd>&mdash;</dd>", file = file)
		elif len(member['ext']) == 1:
			print(f"<dd>{member['ext'][0]}</dd>", file = file)
		else:
			print("<dd><ul>", file = file)
			for ext in member['ext']:
				print(f"<li>{ext}</li>", file = file)
			print("</ul></dd>", file = file)
		print("<dl>\n<dt>Magic code</td>", file = file)
		if len(member.get('magic', [])) == 0:
			print("<dd>&mdash;</dd>", file = file)
		elif len(member['magic']) == 1:
			print(f"<dd>{member['magic'][0]}</dd>", file = file)
		else:
			print("<dd><ul>", file = file)
			for magic in member['magic']:
				print(f"<li>{magic}</li>", file = file)
			print("</ul></dd>", file = file)
		print(f"<dl>\n<dt>Architecture</td>\n<dd>{member.get('arch', '?')}</dd>", file = file)
		print("<dl>\n<dt>Operating systems</td>", file = file)
		systems = member.get('sys', [])
		if len(systems) == 0:
			print("<dd>?</dd>", file = file)
		else:
			if len(systems) == 1:
				tag = 'dd'
			else:
				print("<dd><ul>", file = file)
				tag = 'li'
			for system in systems:
				if 'sys_date' in system:
					line = system['sys_date']
				elif 'sys_date_earliest' in system and 'sys_date_latest' in system:
					line = f"between {system['sys_date_earliest']} and {system['sys_date_latest']}"
				elif 'sys_date_latest' in system:
					line = f"by {system['sys_date_latest']}"
				elif 'sys_date_earliest' in system:
					line = f"after {system['sys_date_earliest']}"
				else:
					line = "?"
				line += f": {system['sys']}"
				if 'sys_target' in system:
					line += f" for {system['sys_target']}" # TODO
				if 'sys_until' in system:
					line += f" until {system['sys_until']}" # TODO: fetch date?
				if 'sys_before' in system:
					line += f" before {system['sys_before']}" # TODO: fetch date?
				print(f"<{tag}>{line}</{tag}>", file = file)
			if len(systems) != 1:
				print("</ul></dd>", file = file)
		print("</dl>", file = file)
		print(f"<dl>\n<dt>Influences</td>\n<dd>{member.get('arch', '&mdash;')}</dd>", file = file)

		document = DOCUMENTS.get(member.get('fmt'))
		if document is None:
			continue

		print(f"""<a id="{fmt}__contents"/>
<h{member['.level'] + 1}>Contents</h1>
<ol>
<li><a href="#{fmt}__contents">Contents</a>""", file = file)

		last_level = 1
		for section in document.sections:
			if last_level < section.level:
				assert section.level == last_level + 1
				print("<ol>", file = file)
			else:
				print("</li>", file = file)
				while last_level > section.level:
					print("</ol></li>", file = file)
					last_level -= 1
			print(f"<li><a href=\"#{fmt}_{make_ref(section.idn)}\">{section.title}</a>", file = file)
			last_level = section.level
		while last_level > 1:
			print("</ol></li>", file = file)
			last_level -= 1
		print(f"""</li><li><a href="#{fmt}__references">References</a></li>
</ol>""", file = file)
		for section in document.sections:
			#print("<hr/>", file = file)
			print(f"<a id=\"{fmt}_{make_ref(section.idn)}\"/>", file = file)
			print(f"<h{member['.level'] + section.level}>{section.title}</h{section.level}>", file = file)
			table = False

			option_count = 1
			for subrow in section.content:
				if type(subrow) is Row:
					if type(subrow.offset) is tuple:
						assert option_count in {1, len(subrow.offset)}
						option_count = len(subrow.offset)
					if type(subrow.type) is tuple:
						assert option_count in {1, len(subrow.type)}
						option_count = len(subrow.type)

			for para in section.content:
				if type(para) is str:
					if table:
						print("</table>", file = file)
						table = False
					print(f"<p>{document.convert_text(para)}</p>", file = file)
				else:
					if not table:
						print("<table border='1' align='center'>", file = file)
						table = True
					print_row(document, para, option_count = option_count, file = file)
			if table:
				print("</table>", file = file)
		#print("""<hr/>
		print(f"""<a id="{fmt}__references"/>
<h{member['.level'] + 1}>References</h1>
<ul>""", file = file)
		for reference in document.references:
			if reference.url is None:
				print(f"<li>[{reference.number}] {reference.title if reference.title is not None else reference.url}</li>", file = file)
			else:
				print(f"<li id=\"{fmt}_{reference.idn}\">[{reference.number}] <a href=\"{reference.url}\" target='_blank'>{reference.title}</a></li>", file = file)
		print("</ul>", file = file)

print("""</body>
</html>""", file = file)
file.close()

