# -*- coding: utf-8 -*-

from flask import Markup, render_template_string


def write_localfile(path, content, is_markup=True):
    with open(path, 'w', encoding='utf-8') as f:
        if is_markup:
            content = Markup(content)
        f.write(content)


def read_localfile(path, is_render=True):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        if is_render:
            content = render_template_string(content)

    return content
