from os.path import abspath
from pathlib import Path
from typing import IO, Generator

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import StreamingResponse
from starlette.routing import Route

"""
Stream a file, in this case an mp4 video, supporting range-requests using starlette

Reference: https://stackoverflow.com/questions/33208849/python-django-streaming-video-mp4-file-using-httpresponse
"""

VIDEO_PATH = "AudioIntensityViz\\media\\"


def ranged \
                (
                file: IO[bytes],
                start: int = 0,
                end: int = None,
                block_size: int = 8192,
        ) -> Generator[bytes, None, None]:
    consumed = 0

    file.seek(start)

    while True:
        data_length = min(block_size, end - start - consumed) if end else block_size

        if data_length <= 0:
            break

        data = file.read(data_length)

        if not data:
            break

        consumed += data_length

        yield data

    if hasattr(file, 'close'):
        file.close()


def homepage(request: Request) -> StreamingResponse:
    videopath = request.path_params['videopath']
    path = Path(VIDEO_PATH + videopath)
    print(abspath(path))
    file = path.open('rb')

    file_size = path.stat().st_size

    content_range = request.headers.get('range')

    content_length = file_size
    status_code = 200
    headers = {}

    if content_range is not None:
        content_range = content_range.strip().lower()

        content_ranges = content_range.split('=')[-1]

        range_start, range_end, *_ = map(str.strip, (content_ranges + '-').split('-'))

        range_start = max(0, int(range_start)) if range_start else 0
        range_end = min(file_size - 1, int(range_end)) if range_end else file_size - 1

        content_length = (range_end - range_start) + 1

        file = ranged(file, start=range_start, end=range_end + 1)

        status_code = 206

        headers['Content-Range'] = f'bytes {range_start}-{range_end}/{file_size}'

    response = StreamingResponse \
            (
            file,
            media_type='video/mp4',
            status_code=status_code,
        )

    response.headers.update \
            ({
            'Accept-Ranges': 'bytes',
            'Content-Length': str(content_length),
            **headers,
        })

    return response


app = Starlette \
        (
        routes= \
            [
                Route('/{videopath}', homepage),
            ],
    )

# class Server(uvicorn.Server):
#     def install_signal_handlers(self):
#         pass
#
#     @contextlib.contextmanager
#     def run_in_thread(self):
#         thread = threading.Thread(target=self.run)
#         thread.start()
#         try:
#             while not self.started:
#                 time.sleep(1e-3)
#             yield
#         finally:
#             self.should_exit = True
#             thread.join()
#
#
# config = Config("AudioIntensityViz.mediaServe:app", host="0.0.0.0", port=5000, log_level="info")
# server = Server(config=config)
