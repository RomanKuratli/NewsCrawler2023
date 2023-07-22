import math
from calendar import month_name

import matplotlib.pyplot as plt
from matplotlib.backends.backend_svg import FigureCanvasSVG as FigureCanvas
from io import BytesIO
from flask import Markup

from analysis import statistics as stat
import mongo_db as db


def get_tags_in_body(soup):
    body_html = ""
    for tag in soup.body.find_all():
        body_html += str(tag)
    return body_html


def get_bar_chart_markup(labels, values, chart_range=None):
    # With a bit of friendly help by ChatGPT
    values = [0 if math.isnan(x) else x for x in values]
    
    plt.bar(labels, values, color="blue")
    # Rotate labels by 90 degrees so that they don't overlap
    plt.xticks(rotation=90)
    # Adjust the bottom margin to make space for longer labels
    plt.subplots_adjust(bottom=0.3)

    canvas = FigureCanvas(plt.gcf())
    buf = BytesIO()
    canvas.print_svg(buf)
    buf.seek(0)
    svg_string = buf.read().decode()
    buf.close()

    # Clear the figure to reset the state for the next plot
    plt.clf()

    return Markup(svg_string)


# ============= aggregators ======================
def count_docs(docs): return len(docs)


def avg_text_sent(term=None):
    def avg_text_sent2(docs):
        return stat.avg_text_sent(docs, term)
    return avg_text_sent2


def percentage_documents_containing(term):
    def idf_per_term(docs):
        return stat.percentage_documents_containing(term, docs)
    return idf_per_term
# ============= /aggregators =====================


# ============= grouping partial charts ======================
def bar_chart_grouped_by_month(coll_name, aggr_func, chart_range=None):
    labels = [f"{month_name[month]} {year}" for year, month, _ in db.group_by_month(coll_name)]
    values = [aggr_func(docs) for _, _, docs in db.group_by_month(coll_name)]
    return get_bar_chart_markup(labels, values, chart_range)


def bar_chart_grouped_by_section(coll_name, aggr_func, chart_range=None) -> Markup:
    labels = []
    values = []
    for section, docs in db.group_by_section(coll_name).items():
        labels.append(section)
        values.append(aggr_func(docs))
    return get_bar_chart_markup(labels, values, chart_range)
# ============= /grouping partial charts =====================


def article_amount_per_month(coll_name) -> Markup:
    return bar_chart_grouped_by_month(coll_name, count_docs)


def article_amount_per_section(coll_name) -> Markup:
    return bar_chart_grouped_by_section(coll_name, count_docs)


def idf_per_month(term, coll_name) -> Markup:
    return bar_chart_grouped_by_month(coll_name, percentage_documents_containing(term))


def idf_per_section(term, coll_name) -> Markup:
    return bar_chart_grouped_by_section(coll_name, percentage_documents_containing(term))


def avg_sent_per_month(coll_name, term=None) -> Markup:
    return bar_chart_grouped_by_month(coll_name, avg_text_sent(term), chart_range=(-0.5, 0.5))


def avg_sent_per_section(coll_name, term=None) -> Markup:
    return bar_chart_grouped_by_section(coll_name, avg_text_sent(term), chart_range=(-0.5, 0.5))
