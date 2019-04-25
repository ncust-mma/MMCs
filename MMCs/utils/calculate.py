# -*- coding: utf-8 -*-

from random import sample

import numba as nb
from flask import current_app

from MMCs.models import Competition, User


def cal_teacher_task_number():
    """Calculate the max teacher gottn task numbers

    Returns:
        int -- task number
    """
    from math import ceil

    com = Competition.current_competition()
    task_number = ceil(
        len(com.solutions) * current_app.config['SOLUTION_TASK_NUMBER'] / len(User.teachers()))

    return task_number


@nb.jit
def gen_teacher_view(this_problem):
    """Generate such as {teacher id: {problem : number}} dictionary

    Arguments:
        this_problem {str} -- current solution problem
    """

    teachers_view = {}
    is_notempty = 0
    for teacher in User.teachers():
        teacher_tasks = teacher.current_all_tasks
        if len(teacher_tasks) < cal_teacher_task_number():
            teacher_task_problems = teacher.current_task_problems
            teachers_view[teacher.id] = teacher_task_problems
            is_notempty += teacher_task_problems[this_problem]

    return teachers_view, is_notempty


@nb.jit
def _random_sample(this_problem, teachers_view, is_notempty):
    """Get random sample teacher to task

    Arguments:
        this_problem {str} -- current solution problem
        teachers_view {dic} -- a data structure
        is_notempty {bool} -- teachers_view no empty flag

    Returns:
        list -- sample teachers' id
    """

    solution_task_number = current_app.config['SOLUTION_TASK_NUMBER']
    if is_notempty:
        teacher_ids = []
        for teacher_id, teacher_problem in teachers_view.items():
            if (len(teacher_ids) <= solution_task_number and
                    teacher_problem[this_problem] and
                    teacher_problem[this_problem] < cal_teacher_task_number()):
                teacher_ids.append(teacher_id)
    else:
        teacher_ids = sample(teachers_view.keys(), solution_task_number)

    return teacher_ids


def random_sample(this_problem):
    """front function, api for `_random_sample`
    """

    teachers_view, is_notempty = gen_teacher_view(this_problem)

    return _random_sample(this_problem, teachers_view, is_notempty)
