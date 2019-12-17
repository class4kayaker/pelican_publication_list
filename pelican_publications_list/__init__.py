""""
Pelican Publication List
========================

A Pelican plugin that populates the context with a list of formatted
citations and related data, loaded from a BibTeX file at a configurable path.

The use case for now is to generate a ``Publications'' page for academic
websites.
"""

import pelican
import citeproc
import bibtexparser
import operator
import warnings

import logging

logger = logging.getLogger(__name__)

__version__ = "0.2.1"


def cite_warn(citation_item):
    logger.warning(
        "WARNING: Reference with key '%s'" " not found in the bibliography.",
        citation_item.key,
    )


def sort_entries(entries, sort_type):
    if sort_type == "key":
        return sorted(entries, key=operator.itemgetter("id"))
    elif sort_type == "date":

        def sort_key(e):
            return (int(e.get("year", 0)), month_ord(e.get("month", "jan")))

        return sorted(entries, key=sort_key, reverse=True)
    elif sort_type == "name":

        def sort_key(e):
            return e.get("author", "")

        return sorted(entries, key=sort_key)
    else:
        raise ValueError("Invalid sort option: {0}".format(sort_type))


def month_ord(month_name):
    normalised_name = month_name[0:3].lower()
    months = [
        "jan",
        "feb",
        "mar",
        "apr",
        "may",
        "jun",
        "jul",
        "aug",
        "sep",
        "oct",
        "nov",
        "dec",
    ]
    month_ords = dict((name, i) for i, name in enumerate(months))
    return month_ords[normalised_name]


def add_publications(generator):
    """
    Populates context with a list of BibTeX publications.

    Configuration
    -------------
    generator.settings['PUBLICATIONS_SRC']:
        local path to the BibTeX file to read.

    Output
    ------
    generator.context['publications']:
        List of tuples (key, entry, record, external).
        See Readme.md for more details.
    """

    if "PUBLICATIONS_SRC" not in generator.settings:
        return
    if "PUBLICATIONS_STYLE" not in generator.settings:
        return

    refs_file = generator.settings["PUBLICATIONS_SRC"]
    refs_style = generator.settings["PUBLICATIONS_STYLE"]
    refs_sort = generator.settings.get("PUBLICATIONS_SORT", "date")

    supress_warning = generator.settings.get(
        "PUBLICATIONS_SUPRESS_BIBTEX_WARNING", True
    )

    with open(refs_file, "r") as fp:
        bibtex_data = bibtexparser.load(fp)

    try:
        entries = sort_entries(bibtex_data.entries, refs_sort)
    except ValueError as e:
        logger.error("%s", e)
        return

    unknown_bib_field = "Unsupported BibTeX field"

    with warnings.catch_warnings(record=True) as w_list:
        citeproc_data = citeproc.source.bibtex.BibTeX(refs_file)
        for w in w_list:
            if supress_warning and unknown_bib_field in str(w.message):
                logger.info("Warning in citeproc-py '%s'", w.message)
            else:
                logger.warning("Warning in citeproc-py '%s'", w.message)

    citeproc_style = citeproc.CitationStylesStyle(refs_style, validate=False)

    if not citeproc_style.has_bibliography():
        logger.warning("Style '%s'  does not include a bibliography", refs_style)
        return

    bibliography = citeproc.CitationStylesBibliography(
        citeproc_style, citeproc_data, citeproc.formatter.html
    )

    cite = {}

    for record in entries:
        key = record["ID"].lower()
        cite["key"] = citeproc.Citation([citeproc.CitationItem(key)])
        bibliography.register(cite["key"])

    for key in bibliography.keys:
        bibliography.cite(cite["key"], cite_warn)

    bibitems = {}
    for key, item in zip(bibliography.keys, bibliography.bibliography()):
        bibitems[key] = str(item)

    publications = []

    for record in entries:
        key = record["ID"].lower()
        entry = bibitems[key]
        external = {}
        if "eprinttype" in record and "eprint" in record:
            if record["eprinttype"] == "arxiv":
                if "eprintclass" in record:
                    external[
                        "ARXIV"
                    ] = "http://arxiv.org/abs/{eprintclass}/{eprint}".format(**record)
                else:
                    external["ARXIV"] = "http://arxiv.org/abs/{eprint}".format(**record)
        if "doi" in record and record["doi"] not in entry:
            external["DOI"] = record["doi"]

        publications.append((key, entry, record, external))
    generator.context["publications"] = publications


def register():
    pelican.signals.generator_init.connect(add_publications)
