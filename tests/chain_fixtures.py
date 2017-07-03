
# -*- coding: utf-8 -*-

import numpy as np

BASIC_CHAIN_STR = ('Chain...\nName:            chain\nOrientation:     None'
                   '\nX:               None\nY:               None'
                   '\nNumber of views: None')

X_INDEX = [(u'q5_1', u'All'), (u'q5_1', 1L), (u'q5_1', 2L),
           (u'q5_1', 3L), (u'q5_1', 4L), (u'q5_1', 5L), (u'q5_1', 97L),
           (u'q5_1', 98L), (u'q5_1', u'mean'), (u'q5_1', u'median')]

X_INDEX_PAINTED = [(u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                    u'Base'),
                   (u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                    u'I would refuse if asked'),
                   (u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                    u'Very unlikely'),
                   (u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                    u"Probably wouldn't"),
                   (u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                    u'Probably would if asked'),
                   (u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                    u'Very likely'),
                   (u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                    u"I'm already planning to"),
                   (u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                    u"Don't know"),
                   (u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                    u'Mean'),
                   (u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                    u'Median')]

EXPECTED_X_BASIC = ([[[250.0, 81.0, 169.0], [11.0, 4.0, 7.0],
                      [20.0, 5.0, 15.0], [74.0, 30.0, 44.0], [0.0, 0.0, 0.0],
                      [74.0, 24.0, 50.0], [10.0, 4.0, 6.0], [61.0, 14.0, 47.0],
                      [30.364, 24.493827160493826, 33.17751479289941],
                      [5.0, 5.0, 5.0]],
                    X_INDEX,
                    [(u'q5_1', u'@'), (u'q4', 1L), (u'q4', 2L)],
                    X_INDEX_PAINTED,
                    [(u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                      u'Total'),
                     ((u'q4. Do you ever participate in sports activities '
                       u'with people in your household?'),
                      u'Yes'),
                     ((u'q4. Do you ever participate in sports activities '
                       u'with people in your household?'),
                      u'No')]], )

EXPECTED_X_NEST_1 = ([[[250.0, 53.0, 28.0, 81.0, 88.0],
                       [11.0, 2.0, 2.0, 5.0, 2.0], [20.0, 2.0, 3.0, 7.0, 8.0],
                       [74.0, 19.0, 11.0, 21.0, 23.0],
                       [0.0, 0.0, 0.0, 0.0, 0.0],
                       [74.0, 19.0, 5.0, 21.0, 29.0],
                       [10.0, 4.0, 0.0, 2.0, 4.0],
                       [61.0, 7.0, 7.0, 25.0, 22.0],
                       [30.364, 23.245283018867923, 26.857142857142858,
                        34.95061728395062, 31.545454545454547],
                       [5.0, 5.0, 3.0, 5.0, 5.0]],
                      X_INDEX,
                      [(u'#pad-0', u'#pad-0', u'q5_1', u'@'),
                       (u'q4', 1L, u'gender', 1L), (u'q4', 1L, u'gender', 2L),
                       (u'q4', 2L, u'gender', 1L), (u'q4', 2L, u'gender', 2L)],
                      X_INDEX_PAINTED,
                      [(u'#pad-0', u'#pad-0',
                        u'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                        u'Total'),
                       ((u'q4. Do you ever participate in sports activities '
                         u'with people in your household?'),
                        u'Yes', u'gender. What is your gender?', u'Male'),
                       ((u'q4. Do you ever participate in sports activities '
                         u'with people in your household?'),
                        u'Yes', u'gender. What is your gender?', u'Female'),
                       ((u'q4. Do you ever participate in sports activities '
                         u'with people in your household?'),
                        u'No', u'gender. What is your gender?', u'Male'),
                       ((u'q4. Do you ever participate in sports activities '
                         u'with people in your household?'),
                        u'No', u'gender. What is your gender?', u'Female')]], )

EXPECTED_X_NEST_2 = ([[[250.0, 12.0, 15.0, 7.0, 8.0, 11.0, 3.0, 6.0, 6.0, 6.0,
                        7.0, 20.0, 12.0, 16.0, 17.0, 16.0, 21.0, 23.0, 21.0,
                        9.0, 14.0],
                       [11.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0],
                       [20.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0,
                        1.0, 1.0, 3.0, 0.0, 2.0, 3.0, 3.0, 2.0, 0.0, 0.0],
                       [74.0, 1.0, 7.0, 3.0, 4.0, 4.0, 2.0, 4.0, 2.0, 1.0, 2.0,
                        4.0, 6.0, 5.0, 4.0, 2.0, 5.0, 6.0, 5.0, 2.0, 5.0],
                       [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                       [74.0, 6.0, 3.0, 1.0, 2.0, 7.0, 1.0, 0.0, 1.0, 1.0, 2.0,
                        7.0, 2.0, 3.0, 6.0, 3.0, 8.0, 7.0, 5.0, 2.0, 7.0],
                       [10.0, 1.0, 2.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0],
                       [61.0, 4.0, 1.0, 2.0, 0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0,
                        7.0, 2.0, 4.0, 5.0, 7.0, 4.0, 5.0, 7.0, 5.0, 1.0],
                       [30.364, 43.5, 22.066666666666666, 30.142857142857142,
                        15.125, 4.2727272727272725, 3.6666666666666665,
                        18.666666666666668, 34.833333333333336,
                        34.333333333333336, 30.571428571428573, 36.8,
                        18.916666666666668, 26.8125, 37.05882352941177,
                        50.5625, 26.19047619047619, 28.130434782608695,
                        39.42857142857143, 56.22222222222222, 17.5],
                       [5.0, 5.0, 3.0, 3.0, 3.0, 5.0, 3.0, 3.0, 4.0, 4.0, 5.0,
                        5.0, 3.0, 3.0, 5.0, 51.0, 5.0, 5.0, 5.0, 98.0, 5.0]],
                      X_INDEX,
                      [('#pad-0', '#pad-0', '#pad-0', '#pad-0', 'q5_1', '@'),
                       ('q4', 1L, 'gender', 1L, 'Wave', 1L),
                       ('q4', 1L, 'gender', 1L, 'Wave', 2L),
                       ('q4', 1L, 'gender', 1L, 'Wave', 3L),
                       ('q4', 1L, 'gender', 1L, 'Wave', 4L),
                       ('q4', 1L, 'gender', 1L, 'Wave', 5L),
                       ('q4', 1L, 'gender', 2L, 'Wave', 1L),
                       ('q4', 1L, 'gender', 2L, 'Wave', 2L),
                       ('q4', 1L, 'gender', 2L, 'Wave', 3L),
                       ('q4', 1L, 'gender', 2L, 'Wave', 4L),
                       ('q4', 1L, 'gender', 2L, 'Wave', 5L),
                       ('q4', 2L, 'gender', 1L, 'Wave', 1L),
                       ('q4', 2L, 'gender', 1L, 'Wave', 2L),
                       ('q4', 2L, 'gender', 1L, 'Wave', 3L),
                       ('q4', 2L, 'gender', 1L, 'Wave', 4L),
                       ('q4', 2L, 'gender', 1L, 'Wave', 5L),
                       ('q4', 2L, 'gender', 2L, 'Wave', 1L),
                       ('q4', 2L, 'gender', 2L, 'Wave', 2L),
                       ('q4', 2L, 'gender', 2L, 'Wave', 3L),
                       ('q4', 2L, 'gender', 2L, 'Wave', 4L),
                       ('q4', 2L, 'gender', 2L, 'Wave', 5L)],
                      X_INDEX_PAINTED,
                      [('#pad-0', '#pad-0', '#pad-0', '#pad-0',
                        'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                        'Total'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 1'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 2'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 3'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 4'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 5'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 1'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 2'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 3'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 4'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 5'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 1'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 2'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 3'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 4'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 5'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 1'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 2'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 3'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 4'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 5')]], )

EXPECTED_X_NEST_3 = ([[[250.0, 12.0, 15.0, 7.0, 8.0, 11.0, 3.0, 6.0, 6.0, 6.0,
                        7.0, 20.0, 12.0, 16.0, 17.0, 16.0, 21.0, 23.0, 21.0,
                        9.0, 14.0, 11.0, 20.0, 74.0, 0.0, 74.0, 10.0, 61.0,
                        53.0, 28.0, 81.0, 88.0],
                       [11.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 0.0,
                        1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0, 11.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0, 5.0, 2.0],
                       [20.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0,
                        1.0, 1.0, 3.0, 0.0, 2.0, 3.0, 3.0, 2.0, 0.0, 0.0, 0.0,
                        20.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.0, 3.0, 7.0, 8.0],
                       [74.0, 1.0, 7.0, 3.0, 4.0, 4.0, 2.0, 4.0, 2.0, 1.0, 2.0,
                        4.0, 6.0, 5.0, 4.0, 2.0, 5.0, 6.0, 5.0, 2.0, 5.0, 0.0,
                        0.0, 74.0, 0.0, 0.0, 0.0, 0.0, 19.0, 11.0, 21.0, 23.0],
                       [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                       [74.0, 6.0, 3.0, 1.0, 2.0, 7.0, 1.0, 0.0, 1.0, 1.0, 2.0,
                        7.0, 2.0, 3.0, 6.0, 3.0, 8.0, 7.0, 5.0, 2.0, 7.0, 0.0,
                        0.0, 0.0, 0.0, 74.0, 0.0, 0.0, 19.0, 5.0, 21.0, 29.0],
                       [10.0, 1.0, 2.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                        0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 1.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 10.0, 0.0, 4.0, 0.0, 2.0, 4.0],
                       [61.0, 4.0, 1.0, 2.0, 0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0,
                        7.0, 2.0, 4.0, 5.0, 7.0, 4.0, 5.0, 7.0, 5.0, 1.0, 0.0,
                        0.0, 0.0, 0.0, 0.0, 0.0, 61.0, 7.0, 7.0, 25.0, 22.0],
                       [30.364, 43.5, 22.066666666666666, 30.142857142857142,
                        15.125, 4.2727272727272725, 3.6666666666666665,
                        18.666666666666668, 34.833333333333336,
                        34.333333333333336, 30.571428571428573, 36.8,
                        18.916666666666668, 26.8125, 37.05882352941177,
                        50.5625, 26.19047619047619, 28.130434782608695,
                        39.42857142857143, 56.22222222222222, 17.5, 1.0, 2.0,
                        3.0, np.NaN, 5.0, 97.0, 98.0, 23.245283018867923,
                        26.857142857142858, 34.95061728395062,
                        31.545454545454547],
                       [5.0, 5.0, 3.0, 3.0, 3.0, 5.0, 3.0, 3.0, 4.0, 4.0, 5.0,
                        5.0, 3.0, 3.0, 5.0, 51.0, 5.0, 5.0, 5.0, 98.0, 5.0,
                        1.0, 2.0, 3.0, 0.0, 5.0, 97.0, 98.0, 5.0, 3.0, 5.0,
                        5.0]],
                      X_INDEX,
                      [('#pad-0', '#pad-0', '#pad-0', '#pad-0', 'q5_1', '@'),
                       ('q4', 1L, 'gender', 1L, 'Wave', 1L),
                       ('q4', 1L, 'gender', 1L, 'Wave', 2L),
                       ('q4', 1L, 'gender', 1L, 'Wave', 3L),
                       ('q4', 1L, 'gender', 1L, 'Wave', 4L),
                       ('q4', 1L, 'gender', 1L, 'Wave', 5L),
                       ('q4', 1L, 'gender', 2L, 'Wave', 1L),
                       ('q4', 1L, 'gender', 2L, 'Wave', 2L),
                       ('q4', 1L, 'gender', 2L, 'Wave', 3L),
                       ('q4', 1L, 'gender', 2L, 'Wave', 4L),
                       ('q4', 1L, 'gender', 2L, 'Wave', 5L),
                       ('q4', 2L, 'gender', 1L, 'Wave', 1L),
                       ('q4', 2L, 'gender', 1L, 'Wave', 2L),
                       ('q4', 2L, 'gender', 1L, 'Wave', 3L),
                       ('q4', 2L, 'gender', 1L, 'Wave', 4L),
                       ('q4', 2L, 'gender', 1L, 'Wave', 5L),
                       ('q4', 2L, 'gender', 2L, 'Wave', 1L),
                       ('q4', 2L, 'gender', 2L, 'Wave', 2L),
                       ('q4', 2L, 'gender', 2L, 'Wave', 3L),
                       ('q4', 2L, 'gender', 2L, 'Wave', 4L),
                       ('q4', 2L, 'gender', 2L, 'Wave', 5L),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1', 'q5_1', 1L),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1', 'q5_1', 2L),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1', 'q5_1', 3L),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1', 'q5_1', 4L),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1', 'q5_1', 5L),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1', 'q5_1', 97L),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1', 'q5_1', 98L),
                       ('#pad-2', '#pad-2', 'q4', 1L, 'gender', 1L),
                       ('#pad-2', '#pad-2', 'q4', 1L, 'gender', 2L),
                       ('#pad-2', '#pad-2', 'q4', 2L, 'gender', 1L),
                       ('#pad-2', '#pad-2', 'q4', 2L, 'gender', 2L)],
                      X_INDEX_PAINTED,
                      [('#pad-0', '#pad-0', '#pad-0', '#pad-0',
                        'q5_1. How likely are you to do each of the following in the next year? - Surfing',
                        'Total'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 1'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 2'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 3'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 4'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 5'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 1'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 2'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 3'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 4'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 5'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 1'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 2'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 3'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 4'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Male',
                        'Wave. Wave', u'Wave 5'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 1'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 2'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 3'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 4'),
                       (('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Female',
                        'Wave. Wave', u'Wave 5'),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1',
                        ('q5_1. How likely are you to go surfing in the next '
                        'year?'),
                        u'I would refuse if asked'),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1',
                        ('q5_1. How likely are you to go surfing in the next '
                        'year?'),
                        u'Very unlikely'),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1',
                        ('q5_1. How likely are you to go surfing in the next '
                        'year?'),
                        u"Probably wouldn't"),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1',
                        ('q5_1. How likely are you to go surfing in the next '
                        'year?'),
                        u'Probably would if asked'),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1',
                        ('q5_1. How likely are you to go surfing in the next '
                        'year?'),
                        u'Very likely'),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1',
                        ('q5_1. How likely are you to go surfing in the next '
                        'year?'),
                        u"I'm already planning to"),
                       ('#pad-1', '#pad-1', '#pad-1', '#pad-1',
                        ('q5_1. How likely are you to go surfing in the next '
                        'year?'),
                        u"Don't know"),
                       ('#pad-2', '#pad-2',
                        ('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Male'),
                       ('#pad-2', '#pad-2',
                        ('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'Yes', 'gender. What is your gender?', u'Female'),
                       ('#pad-2', '#pad-2',
                        ('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Male'),
                       ('#pad-2', '#pad-2',
                        ('q4. Do you ever participate in sports activities '
                         'with people in your household?'),
                        u'No', 'gender. What is your gender?', u'Female')]], )

