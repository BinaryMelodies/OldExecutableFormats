# Documenting old computer executable formats

This project is an on-going attempt to collect as much information as possible on several old executable file formats.
The focus has mostly revolved around old UNIXen, DOS-like systems and related operating systems, as well as 16-bit home computers.

Most of this information is available online, scattered in different locations, but this file also includes information on more obscure and obsolete sources and formats, and in general information that often gets left out from the most up to date documentations.
This document also attempts to provide a diachronic overview, focusing on which versions introduced which entries or features, instead of just presenting the latest versions of each file format.
The author has strived for completeness and preservation of as much information as possible, at the potential detriment of consistency and correctness.

When possible, the runtime memory layout is also mentioned.

## Disclaimer

All information here is presented without any warranty on correctness.

Since the source materials on these file formats aren't always of the highest quality, some misunderstandings and faulty assumptions might have occured in the documentation effort.
As the research on filling in details is on-going, the database is also incomplete.

With that said, the author put in effort to make sure that what is documented here is correct or at the very least plausible and consistent with available documentation.

# HTML Generation

To generate the documentation in the HTML format, you will need to run the following command:

    python3 generate.py execfmt.dat

This will create the HTML file called execfmt.html.

