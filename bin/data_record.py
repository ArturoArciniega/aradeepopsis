#!/usr/bin/env python

import tensorflow as tf

def create_record(image_data, filename, height, width, ratio):
    def _bytes_feature(value):
        if isinstance(value, str):
            value = value.encode()
        return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

    def _int64_feature(value):
      return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

    def _float_feature(value):
        return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))

    features = {
        'image/original': _bytes_feature(image_data),
        'image/filename': _bytes_feature(filename),
        'image/height': _int64_feature(height),
        'image/width': _int64_feature(width),
        'image/resize_ratio': _float_feature(ratio),
        }

    sample = tf.train.Example(features=tf.train.Features(feature=features))
    return sample

def parse_record(record):
    features = {
        'image/original': tf.io.FixedLenFeature((), tf.string),
        'image/filename': tf.io.FixedLenFeature((), tf.string),
        'image/height': tf.io.FixedLenFeature((), tf.int64),
        'image/width': tf.io.FixedLenFeature((), tf.int64),
        'image/resize_ratio': tf.io.FixedLenFeature((), tf.float32)
        }

    parsed = tf.io.parse_single_example(record, features)
    
    image = tf.io.decode_image(parsed['image/original'], channels=3)

    sample = {
    'original': image,
    'filename': parsed['image/filename'],
    'height': parsed['image/height'],
    'width': parsed['image/width'],
    'resize_factor': parsed['image/resize_ratio'],
    }
    return sample