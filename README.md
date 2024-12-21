# Documenting old computer executable formats

This project is an on-going attempt to collect as much information as possible on several old executable file formats.
The focus has mostly revolved around old UNIXen, DOS-like systems and related operating systems, as well as 16-bit home computers.

Most of this information is available online, scattered in different locations, but this file also includes information on more obscure and obsolete sources and formats, and in general information that often gets left out from the most up to date documentations.
This document also attempts to provide a diachronic overview, focusing on which versions introduced which entries or features, instead of just presenting the latest versions of each file format.
The author has strived for completeness and preservation of as much information as possible, at the potential detriment of consistency and correctness.

When possible, the runtime memory layout is also mentioned.

# HTML Generation

The repository already contains a generated HTML file, however it is possible to rerun the generation if needed.
To generate the documentation in the HTML format, you will need to run the following command:

    python3 generate.py execfmt.dat

This will create the HTML file called `execfmt.html`.

# Notes on the database file format

The database file execfmt.dat is stored in an ad-hoc format created specifically to store information about file formats.
It is ultimately undocumented and its semantics are defined by the script `generate.py`, as it evolved together with the database itself.
In order to make reading and extending easier, here are a few pieces of information on the file format.
Beware that if `generate.py` gets updated, this description might become out of date, so consider it only as a general guide.

The database is divided into two parts, the first part listing the file formats and their general properties, the second part giving the more detailed structure of each file format.
The two parts are separated by a line containing only `DESCRIPTIONS`.
Lines starting with the pound/hash mark symbol `#` are ignored.
When generating the HTML files, the first part is used to create a short overview at the top of each section for each file format, with the second part providing the contents.

The first part of the database includes information such as the file format name, year of first public appearance, what systems or architectures it runs on, and when was their support introduced or dropped.
It follows a very simple `.tag:value` format, where `.tag` (always starts with a period) specifies the type of the information and `value` describing the information itself.
The tags have a specific hierarchy to them, with `.fmt` starting a new file format description, and `.sys` introducing a new set of properties specific to that system.
Formats themselves can be organized in the documentation in a hierarchy (for example, Classic Mac OS binaries are stored inside Macintosh Resources, which when stored on a non-Macintosh file system is then stored inside an AppleSingle/AppleDouble container, so the documentation of the AppleSingle/AppleDouble file format is grouped under the Macintosh Resource file format).
The database also contains more speculative information.
For example, since the exact timeline of support can not always be established with the available information, fields such as `sys_date_earliest` and `sys_date_latest` provide the boundary dates between which the file format could have appeared.
The file format influences are rarely mentioned in the available documentation and the entries are based on educated guesses by the author.

The second part of the database contains the detailed descriptions for each file format.
It is organized as a sequence of tables, commands and paragraphs.
Commands (such as `TITLE`, `SECTION`, `REFERENCE`) provide the organization of each format.
The `TITLE` command introduces the file format, while `SECTION` introduces a new subsection in the HTML file.
Both of these take two arguments separated by a colon `:`, the first argument giving a keyword, the second argument the name, as it is to appear in the generated HTML file.
For the `TITLE` command, the keyword must match the name of the format provided in the first half of the file.
Furthermore, `SECTION` commands can be nested, inner sections taking a prefix separated by a slash character `/` indicating the level (1 being the second highest, with increasing numbers providing successive levels of subsections).

Tables usually describe the structure of each part of the file format.
Tables can also be nested inside each other.
Each subtable appears inside the last row, the first level of subtable has to be introduced with two tabulation characters as indentation, and every further one indented with a single tabulation character more.

Paragraphs are introduced with the `>` character in the first column, and followed by the text to be included in the HTML file.

Text within paragraphs and tables may contain internal references.
Aside from HTML `<a>` tags, the curly braces `{` and `}` create links to sections or references contained in the description of the same file format.
For sections, they refer to the keyword argument of the `SECTION` command.
By convention, section keywords are all lowercase, while reference keywords are all uppercase.
This is not enforced by the script and is up to the developer's taste.

The `REFERENCE` command takes three parameters, separated by spaces: the keyword which will be used to link to it, enclosed in braces `{` and `}`, the title as it should appear in the generated HTML file, enclosed within double quote characters `"`, and an optional hyperlink.

# Disclaimer

All information here is presented without any warranty on correctness.

Since the source materials on these file formats aren't always of the highest quality, some misunderstandings and faulty assumptions might have occured in the documentation effort.
As the research on filling in details is on-going, the database is also incomplete.

With that said, the author put in effort to make sure that what is documented here is correct or at the very least plausible and consistent with available documentation.

