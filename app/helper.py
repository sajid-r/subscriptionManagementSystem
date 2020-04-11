import uuid, datetime, boto3, copy
from app import app, logger
from itertools import count
import dateparser
import requests

session = boto3.Session(
	aws_access_key_id=app.config.get("AWS_ACCESS_KEY_ID"),
	aws_secret_access_key=app.config.get("AWS_SECRET_ACCESS_KEY")
)

def rchop(thestring, ending):
	if thestring.endswith(ending):
		return thestring[:-len(ending)]
	return thestring

def get_unique_id():
	return str(uuid.uuid4())

def is_public_content(source):
	public_sources = ['youtube', 'onedrive']
	if source and source.lower() in public_sources:
		return True
	return False

def get_current_time():
	return f"{(datetime.datetime.utcnow().isoformat())}Z"

def convert_utc_time(utc_time, format='%e %b %Y'):
	converted_time = utc_time
	if utc_time:
		converted_time = dateparser.parse(utc_time, settings={'TIMEZONE': 'Asia/Kolkata'}).strftime(format)
	return converted_time

def convert_time(time, includeFormat = False):
	if (time == None or time < 0):
		return ''
	# Hours, minutes and seconds
	hrs = int(time/3600)
	mins = int((time%3600)/60)
	secs = int(time%60)

    # Output like "1:01" or "4:03:59" or "123:03:59"
	ret = ""

	if includeFormat:
		if (hrs > 0) :
		    ret = f"{hrs} hrs "
		if (mins > 0):
			ret = f"{ret}{mins} mins "
		if (secs > 0):
			ret = f"{ret}{secs} secs "
	else:
		if (hrs > 0):
			ret = f"{hrs}:{'0' if mins < 10 else ''}"
		ret = f"{ret}{mins}:{'0' if secs < 10 else ''}"
		ret = f"{ret}{secs}"
	return ret

def get_s3_shareable_link(link):
	signedUrl = None
	if link:
		myBucket = link.split('/')[3]
		myKey = link.split(f"{myBucket}/")[1]
		signedUrl = authenticate_s3_link(myBucket, myKey)
	return signedUrl

def authenticate_s3_link(bucket, key, expires_in = None):
	signedUrl = None
	if expires_in == None:
		expires_in = 60 * 24; # your expiry time in seconds.
	try:
		s3 = session.client("s3")
		signedUrl = s3.generate_presigned_url('get_object', Params = {
			'Bucket': bucket,
			'Key': key
		}, ExpiresIn = expires_in)
	except Exception as e:
		logger.error('S3_AUTH', message=e, exc_info=True)
		return None
	return signedUrl


def divide_chunks(l, n):
	# Yield successive n-sized
	# chunks from l.
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

class PaginatedCursor(object):
    def __init__(self, cur, limit=100):
        self.cur = cur
        self.limit = limit
        self.count = cur.count()

    def __iter__(self):
        skipper = count(start=0, step=self.limit)

        for skip in skipper:
            if skip >= self.count:
                break

            for document in self.cur.skip(skip).limit(self.limit):
                yield document

            self.cur.rewind()