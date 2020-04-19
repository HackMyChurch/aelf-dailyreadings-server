# -*- coding: utf-8 -*-
'''
Generic office / lecture accessors.

TODO: rewrite as a class
'''

from collections import namedtuple

#
# TYPES
#

LecturePosition = namedtuple('LecturePosition', ['officeVariantIdx', 'lectureVariantIdx', 'lectureVariants'])

#
# API
#

def get_lectures_variants_by_type(data, name):
    '''
    Find all lectures of type ``name``. Return a list of ``(office_variant_idx, lecture_variant_idx, lectureVariants)``
    '''
    out = []
    for office_variant_idx, variant in enumerate(data['variants']):
        for lecture_variant_idx, lectureVariants in enumerate(variant['lectures']):
            if lectureVariants[0]['key'] == name:
                out.append(LecturePosition(office_variant_idx, lecture_variant_idx, lectureVariants))
    return out

def get_lecture_variants_by_type(data, name):
    '''
    Find first lecture element with type ``name`` or return None
    '''
    lectures = get_lectures_variants_by_type(data, name)
    if lectures:
        return lectures[0]
    return None

def insert_lecture_variants_before(data, lectureVariants, before):
    '''
    Insert raw ``lectureVariants`` dict before ``before`` LecturePosition object
    '''
    data['variants'][before.officeVariantIdx]['lectures'].insert(before.lectureVariantIdx, lectureVariants)

def insert_lecture_variants_after(data, lectureVariants, after):
    '''
    Insert raw ``lectureVariants`` dict after ``after`` LecturePosition object
    '''
    data['variants'][after.officeVariantIdx]['lectures'].insert(after.lectureVariantIdx+1, lectureVariants)

