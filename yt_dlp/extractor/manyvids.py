import re

from .common import InfoExtractor
from ..utils import (
    determine_ext,
    extract_attributes,
    int_or_none,
    str_to_int,
    url_or_none,
    urlencode_postdata,
)


class ManyVidsIE(InfoExtractor):
    _VALID_URL = r'(?i)https?://(?:www\.)?manyvids\.com/video/(?P<id>\d+)'
    _TESTS = [{
        # preview video
        'url': 'https://www.manyvids.com/Video/133957/everthing-about-me/',
        'md5': '03f11bb21c52dd12a05be21a5c7dcc97',
        'info_dict': {
            'id': '133957',
            'ext': 'mp4',
            'title': 'everthing about me (Preview)',
            'uploader': 'ellyxxix',
            'view_count': int,
            'like_count': int,
        },
    }, {
        # full video
        'url': 'https://www.manyvids.com/Video/935718/MY-FACE-REVEAL/',
        'md5': 'bb47bab0e0802c2a60c24ef079dfe60f',
        'info_dict': {
            'id': '935718',
            'ext': 'mp4',
            'title': 'MY FACE REVEAL',
            'description': 'md5:ec5901d41808b3746fed90face161612',
            'uploader': 'Sarah Calanthe',
            'view_count': int,
            'like_count': int,
        },
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)
        real_url = 'https://www.manyvids.com/video/%s/gtm.js' % (video_id, )

        webpage = self._download_webpage(
            real_url, video_id, 'Downloading webpage')

        mv_token = self._search_regex(
            r'data-mvtoken=(["\'])(?P<value>(?:(?!\1).)+)\1', webpage,
            'mv token', default=None, group='value')

        if mv_token:
            # Sets some cookies
            self._download_webpage(
                'https://www.manyvids.com/includes/ajax_repository/you_had_me_at_hello.php',
                video_id, note='Setting format cookies', fatal=False,
                data=urlencode_postdata({
                    'mvtoken': mv_token,
                    'vid': video_id,
                }), headers={
                    'Referer': url,
                    'X-Requested-With': 'XMLHttpRequest'
                })

        title = self._search_regex(
            r'''<h1\sclass="VideoMetaInfo_title__mWRak">(.*)</h1>''',
            webpage, 'video title', default='')

        description = self._search_regex(
            r'''<p\sclass="VideoDetail_partial__T9jkc"\sdata-testid="description">([\s\S.]*)</p>''',
            webpage, 'video description', default='')

        model = self._search_regex(
            r'''<a aria-label="model-profile" .*>(.*)</a>''',
            webpage, 'model name', default='')

        video_info_url = f'https://video-player-bff.estore.kiwi.manyvids.com/vercel/videos/{video_id}/private'
        video_info = self._download_json(
            video_info_url, video_id, 'Downloading video info'
        )

        model_info_url = f'<a aria-label="model-profile"'

        formats = [
            {
                'url': video_info['data']['filepath'],
                'format_id': 'original'
            },
        ]

        return {
            'id': video_id,
            'title': title,
            'formats': formats,
            'description': description,
            'uploader': model
        }
