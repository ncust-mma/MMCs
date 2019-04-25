# -*- coding: utf-8 -*-

import os

from flask import abort


def zip2here(input_path, output_path):
    """pack a file or folder to dis path

    Arguments:
        input_path {str}
        output_path {str}
    """

    from zipfile import ZipFile

    with ZipFile(output_path, 'w') as z:
        if os.path.isdir(input_path):
            for root, _, files in os.walk(input_path):
                for file in files:
                    if file == '.gitkeep':
                        continue
                    z.write(os.path.join(root, file), file)

        elif os.path.isfile(input_path):
            z.write(input_path, os.path.split(input_path)[1])
        else:
            abort(404)
