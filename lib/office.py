# -*- coding: utf-8 -*-
'''
Generic office / lecture accessors.

TODO: rewrite as a class
'''

from collections import namedtuple

#
# TYPES
#

LecturePosition = namedtuple('LecturePosition', ['variantIdx', 'lectureIdx', 'lecture'])

#
# API
#

def get_lectures_by_type(data, name):
    '''
    Find all lectures of type ``name``. Return a list of ``(variant_idx, lecture_idx, lecture)``
    '''
    out = []
    for variant_idx, variant in enumerate(data['variants']):
        for lecture_idx, lecture in enumerate(variant['lectures']):
            if lecture['key'] == name:
                out.append(LecturePosition(variant_idx, lecture_idx, lecture))
    return out

def get_lecture_by_type(data, name):
    '''
    Find first lecture element with type ``name`` or return None
    '''
    lectures = get_lectures_by_type(data, name)
    if lectures:
        return lectures[0]
    return None

def insert_lecture_before(data, lecture, before):
    '''
    Insert raw ``lecture`` dict before ``before`` LecturePosition object
    '''
    data['variants'][before.variantIdx]['lectures'].insert(before.lectureIdx, lecture)

def insert_lecture_after(data, lecture, after):
    '''
    Insert raw ``lecture`` dict after ``after`` LecturePosition object
    '''
    data['variants'][after.variantIdx]['lectures'].insert(after.lectureIdx+1, lecture)

