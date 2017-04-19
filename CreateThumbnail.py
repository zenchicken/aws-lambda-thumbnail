from __future__ import print_function
import boto3
from subprocess import Popen, PIPE
import json
import io
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

VERSION = '0.2.0'

class ResizeError(Exception):
    def __init__(self, message):
        self.message = message


def resize_image(image_obj, width, height, mode,format):
    cmd = [
        'convert',  # ImageMagick Convert
        '-',  # Read original picture from StdIn
        '-auto-orient',  # Detect picture orientation from metadata
        '-thumbnail', '{}x{}{}'.format(width, height, mode),  # Thumbnail size
        '-extent', '{}x{}'.format(width, height),  # Fill if original picture is smaller than thumbnail
        '-gravity', 'Center',  # Extend (fill) from the thumbnail middle
        '-unsharp',' 0x.5',  # Un-sharpen slightly to improve small thumbnails
        '-quality', '80%',  # Thumbnail JPG quality
        '{}:-'.format(format),  # Write thumbnail with `format` to StdOut
    ]

    logger.info("Executing [{}]".format(cmd))
    p = Popen(cmd, stdout=PIPE, stdin=PIPE)
    thumbnail = p.communicate(input=image_obj.getvalue())[0]

    if not thumbnail:
        logger.error('Error occured. `thumbnail` was nil')
        raise ResizeError('Image format not supported')
    else:
        return thumbnail

def read_s3_stream(bucket, key):
    logger.info("Downloading s3://{}/{}".format(bucket, key))
    file = io.BytesIO()
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, key)
    obj.download_fileobj(file)
    return file

def write_s3_stream(bucket, key, file, contenttype):
    logger.info("Writing s3://{}/{}".format(bucket, key))
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=file,
        ContentType=contenttype
    )


def lambda_handler(event, context):
    source_bucket = event['source_bucket']
    source_key = event['source_key']
    dest_bucket = event['dest_bucket']
    dest_key = event['dest_key']
    height = event['height']
    width = event['width']
    mode = event['mode']
    format = event['format']

    logger.info('Thumbnail (Lambda) - v{}'.format(VERSION))
    logger.debug('  Event: {}'.format(event))
    logger.debug('  Context: {}'.format(context))

    input = read_s3_stream(source_bucket, source_key)
    output = resize_image(input, width, height, mode, format)
    write_s3_stream(dest_bucket, dest_key, output, 'image/{}'.format(format))

    return {
        'result': 'success'
    }
