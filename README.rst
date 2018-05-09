Pelican Publication List
========================

Pelican plugin to add a list of publications to the generator environment to use in templates.
The list of publications is in the variable 'publications', and consists of
a list of tuples of the following form: ``(key, formatted_entry, bibtex_record,
external_links)``.

Due to citeproc-py not including all Bibtex keys in its parsed representation
of the files, and bibparser not including any citation formatting logic, both
are used to parse the bibtex file, and the citation keys are then used to
associate the two representations.

Options
-------

PUBLICATIONS_SRC
    Bibtex file with full publications list

PUBLICATIONS_STYLE
    CSL style file for reference formatting

PUBLICATIONS_SORT
    Key to sort references by, should be one of 'key', 'date', 'name' or
    'author'. Default is 'date'.

External Links
--------------

As the plugin is intended to generate a list of publications for an academic website, in addition to exposing the original bibtex record, a list of convenient URL locations is exposed.

DOI
    Added if the 'doi' field is provided and reproduces it exactly.
ARXIV
    Added if 'eprinttype' is 'arxiv' and consists of a URL pointing to the indicated location on arXiv.

Example Template Fragment
-------------------------

.. code-block:: html5
    <div class="ref-list">
    <h2>Publications</h2>
        {% for key, entry, record, external in publications %}
        <div id="{{ key }}"><span>{{ entry }} </span>
            {% if external.DOI is defined -%}
            <span><a class="DOI" href="{{ external.DOI }}">DOI</a> </span>
            {%- endif -%}
            {% if external.ARXIV is defined -%}
            <span><a class="ARXIV" href="{{ external.DOI }}">ARXIV</a></span>
            {%- endif -%}
            {% if record.link is defined %}
            <span><a href="{{ publication.link }}">Full Text</a> </span>
            {% endif %}
        </div>
        {% endfor %}
    </div>

