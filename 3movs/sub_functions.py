import boto3
import configs
from loggers import error_logger as elgr

s3 = boto3.resource(
    "s3",
    endpoint_url="https://s3.us-west-1.wasabisys.com",
    aws_access_key_id="WKLBE5JBZU3F6XGWQM7A",
    aws_secret_access_key="W0UYDYsJWO5mGmREI3BwTZAgQBy63NVdtnezTtLc",
)

boto_bucket = s3.Bucket("3movs")


def wasabi(data: bytes, url: str, tp: str):
    ext = url.split(".")[-1]
    with open(configs.PATH + "/temp/temp." + ext, "wb") as temp:
        for i in range(len(data) // 10000 + 1):
            temp.write(data[i * 10000 : (i + 1) * 10000])

    if tp == "photo":
        dirname = "_".join(url.split("/")[-5:-2])
        name = "photos/" + dirname + "/" + url.split("/")[-1]
    else:
        dirname = "_".join(url.split("/")[5:8])
        name = "videos/" + dirname + "/" + "".join(url.split("---")[-1])

    try:
        with open(configs.PATH + "/temp/temp." + ext, "rb") as data:
            boto_bucket.upload_fileobj(data, name)
    except Exception as e:
        elgr.error(f"WASABI ERROR -> {e}")
        raise ConnectionError

    return name
