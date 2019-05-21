# -*- coding: utf-8 -*-

import os

from flask import abort


def zip2here(input_paths, output_path, diff=False):
    """pack a file or folder to dis path

    Arguments:
        input_paths {str}
        output_path {str}
    """

    from zipfile import ZipFile

    with ZipFile(output_path, 'w') as z:
        if not diff:
            for input_path in input_paths:
                file = os.path.join('tasks', os.path.split(input_path)[-1])
                z.write(input_path, file)
        else:
            if os.path.isdir(input_paths):
                for root, _, files in os.walk(input_paths):
                    for file in files:
                        if file == '.gitkeep':
                            continue
                        z.write(os.path.join(root, file), file)

            elif os.path.isfile(input_paths):
                z.write(input_paths, os.path.split(input_paths)[1])
            else:
                abort(404)
