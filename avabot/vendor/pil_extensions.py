# -*- coding: utf-8 -*-


def draw_rectangle(context, pos, outline=None, width=1):
    rect_pos = pos
    for i in xrange(width):
        context.rectangle(rect_pos, outline=outline)
        rect_pos = [c + 1 for c in rect_pos]
    return context


def draw_rectangle_label(context, rect_pos, label, background_color, font_color='white'):
    x_min, y_min, x_max, y_max = rect_pos

    # draw background for our fancy label (top of the rectangle).
    context.line([x_min, y_min, x_max, y_min], fill=background_color, width=12)

    # draw the label on top of the label background.
    label_pos = [x_min + 4, y_min - 6]
    context.text(label_pos, label, fill=font_color)

    return context


def draw_detection_region(context, pos, label, color):
    context = draw_rectangle(context, pos, color)
    context = draw_rectangle_label(context, pos, label, background_color=color)
    return context
