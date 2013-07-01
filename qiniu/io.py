# -*- coding: utf-8 -*-
from base64 import urlsafe_b64encode
import rpc
import conf
try:
	import zlib as binascii
except ImportError:
	import binascii


UNDEFINED_KEY = "?"


class PutExtra(object):
	params = {}
	mime_type = 'application/octet-stream'
	crc32 = ""
	check_crc = 0


def put(uptoken, key, data, extra=None):
	""" put your data to Qiniu

	key, your resource key. if key is None, Qiniu will generate one.
	data may be str or read()able object.
	"""
	fields = {
	}

	if not extra:
		extra = PutExtra()

	if extra.params:
		for key in extra.params:
			fields[key] = str(extra.params[key])

	if extra.check_crc:
		fields["crc32"] = str(extra.crc32)

	if key is not None:
		fields['key'] = key

	fields["token"] = uptoken

	fname = key
	if fname is None:
		fname = UNDEFINED_KEY
	elif fname is '':
		fname = 'index.html'
	files = [
		{'filename': fname, 'data': data, 'mime_type': extra.mime_type},
	]
	return rpc.Client(conf.UP_HOST).call_with_multipart("/", fields, files)


def put_file(uptoken, key, localfile, extra=None):
	""" put a file to Qiniu

	key, your resource key. if key is None, Qiniu will generate one.
	"""
	if extra is not None and extra.check_crc == 1:
		extra.crc32 = _get_file_crc32(localfile)
	with open(localfile) as f:
		return put(uptoken, key, f, extra)


def get_url(domain, key, dntoken):
	return "%s/%s?token=%s" % (domain, key, dntoken)


_BLOCK_SIZE = 1024 * 1024 * 4

def _get_file_crc32(filepath):
	with open(filepath) as f: 
		block = f.read(_BLOCK_SIZE)
		crc = 0
		while len(block) != 0:
			crc = binascii.crc32(block, crc) & 0xFFFFFFFF
			block = f.read(_BLOCK_SIZE)
	return crc
