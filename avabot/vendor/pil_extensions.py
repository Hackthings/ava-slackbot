# -*- coding: utf-8 -*-


def draw_rectangle(context, pos, outline=None, width=1):
    rect_pos = pos
    for i in xrange(width):
        context.rectangle(rect_pos, outline=outline)
        rect_pos = [c + 1 for c in rect_pos]
    return context


def draw_detection_region(context, pos, label, color):
    x_min, y_min, x_max, y_max = pos
    label_pos = [x_min + 4, y_max - 12]  # add padding to make text visible.

    draw_rectangle(context, pos, color)
    context.text(label_pos, label, fill=color)
    return context
