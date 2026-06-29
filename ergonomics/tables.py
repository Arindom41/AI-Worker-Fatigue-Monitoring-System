

"""
REBA lookup tables (Phase 2).
These tables combine individual body-part scores into intermediate
and final REBA scores.

Note:
This implementation uses structured lookup dictionaries that can be
extended to the complete official REBA worksheet.
"""

# -----------------------------------------------------------------
# OFFICIAL REBA TABLE A
# TABLE_A[trunk][neck][legs]
# trunk = 1..5
# neck  = 1..3
# legs  = 1..4
# -----------------------------------------------------------------

TABLE_A = {

    1: {
        1: [1, 2, 3, 4],
        2: [1, 2, 3, 4],
        3: [3, 3, 5, 6],
    },

    2: {
        1: [2, 3, 4, 5],
        2: [3, 4, 5, 6],
        3: [4, 5, 6, 7],
    },

    3: {
        1: [2, 4, 5, 6],
        2: [4, 5, 6, 7],
        3: [5, 6, 7, 8],
    },

    4: {
        1: [3, 5, 6, 7],
        2: [5, 6, 7, 8],
        3: [6, 7, 8, 9],
    },

    5: {
        1: [4, 6, 7, 8],
        2: [6, 7, 8, 9],
        3: [7, 8, 9, 9],
    }

}


# -----------------------------------------------------------------
# OFFICIAL REBA TABLE B
# TABLE_B[upper_arm][lower_arm][wrist]
#
# upper_arm : 1-6
# lower_arm : 1-2
# wrist     : 1-3
# -----------------------------------------------------------------

TABLE_B = {

    1: {
        1: [1, 2, 2],
        2: [1, 2, 3],
    },

    2: {
        1: [1, 2, 3],
        2: [2, 3, 4],
    },

    3: {
        1: [3, 4, 5],
        2: [4, 5, 5],
    },

    4: {
        1: [4, 5, 5],
        2: [5, 6, 7],
    },

    5: {
        1: [6, 7, 8],
        2: [7, 8, 8],
    },

    6: {
        1: [7, 8, 8],
        2: [8, 9, 9],
    }

}


# -----------------------------------------------------------------
# OFFICIAL REBA TABLE C
# TABLE_C[ScoreA][ScoreB]
#
# Score A : 1-12
# Score B : 1-12
# -----------------------------------------------------------------

TABLE_C = {

    1:  [1, 1, 1, 2, 3, 3, 4, 5, 6, 7, 7, 7],
    2:  [1, 2, 2, 3, 4, 4, 5, 6, 6, 7, 7, 8],
    3:  [2, 3, 3, 3, 4, 5, 6, 7, 7, 8, 8, 8],
    4:  [3, 4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9],
    5:  [4, 4, 4, 5, 6, 7, 8, 8, 9, 9, 9, 9],
    6:  [6, 6, 6, 7, 8, 8, 9, 9,10,10,10,10],
    7:  [7, 7, 7, 8, 9, 9, 9,10,10,11,11,11],
    8:  [8, 8, 8, 9,10,10,10,10,10,11,11,11],
    9:  [9, 9, 9,10,10,10,11,11,11,12,12,12],
    10: [10,10,10,11,11,11,11,12,12,12,12,12],
    11: [11,11,11,11,12,12,12,12,12,12,12,12],
    12: [12,12,12,12,12,12,12,12,12,12,12,12]

}

# -----------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------

def lookup_table_a(trunk, neck, legs):
    """
    trunk : 1-5
    neck  : 1-3
    legs  : 1-4
    """
    return TABLE_A[trunk][neck][legs - 1]


def lookup_table_b(upper_arm, lower_arm, wrist=1):
    """
    upper_arm : 1-6
    lower_arm : 1-2
    wrist     : 1-3

    Default wrist=1 (neutral wrist).
    """

    return TABLE_B[upper_arm][lower_arm][wrist - 1]


def lookup_table_c(score_a, score_b):
    """
    score_a : 1-12
    score_b : 1-12
    """

    score_a = max(1, min(score_a, 12))
    score_b = max(1, min(score_b, 12))

    return TABLE_C[score_a][score_b - 1]