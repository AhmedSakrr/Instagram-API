from io import BytesIO
from random import randrange
from time import time

from fake_headers import Headers
from PIL import Image
from requests import Session


class InstagramBasic:
    def __init__(self):
        self.domain = 'https://www.instagram.com/'
        self.ses = Session()
        self.ses.headers.update(Headers(headers=True).generate())
        self._loggen_in = False
        self._first_seen_()

    def _first_seen_(self) -> None:
        self.ses.get(self.domain)
        self._working_headers = self.ses.headers

    def _working_headers_(self) -> dict:
        self._working_headers.update({
            'X-CSRFToken': self.ses.cookies.get('csrftoken'),
            'X-IG-App-ID': str(randrange(111111111111111, 999999999999999)),
            'X-IG-WWW-Claim': '0',
            'X-Instagram-AJAX': '191f02aa9d4b',
            'X-Requested-With': 'XMLHttpRequest'
        })
        return self._working_headers

    def _status_check_(self, answer: dict) -> bool:
        if answer['status'] != 'ok':
            return False
        else:
            return True

    def _action_check_(self, action: str, can_do: list) -> bool:
        if action not in can_do:
            print('You can do, only:', can_do)
            return True

    def _check_user_(self, user: str) -> str:
        if user.isnumeric():
            return user

        answer = self.user_info(user)

        if not user:
            return ''
        else:
            return answer['id']

    def _check_post_(self, post: str) -> str:
        '''
        Validating media code. Receive media ID or short code.
        '''

        if post.isnumeric():
            return post

        answer = self.media_info(post)

        if not answer:
            return ''
        else:
            return answer['shortcode_media']['id']

    def _convert_image_(self, photo: bytes) -> bytes:
        '''
        Convert image from .png to .jpg
        '''

        photo = Image.open(BytesIO(photo))
        photo = photo.convert('RGB')
        bts = BytesIO()
        photo.save(bts, format='JPEG')

        return bts.getvalue()

    def _upload_photo_(self, photo: bytes) -> str:
        '''
        Upload photo to Instagram
        '''

        photo = self._convert_image_(photo)
        _id = str(int(time()*1000))
        url = self.domain+'rupload_igphoto/fb_uploader_'+_id

        headers = self._working_headers_().copy()
        headers.update({
            'Content-Type': 'image/jpeg',
            'Offset': '0',
            'X-Entity-Length': str(len(photo)),
            'X-Entity-Name': 'fb_uploader_'+_id,
            'X-Instagram-Rupload-Params': '{"media_type":1,"upload_id":"' +
            _id+'","upload_media_height":1079,"upload_media_width":1080}'
        })

        answer = self.ses.post(
            url, data=photo, headers=headers
        ).json()['upload_id']

        return answer

    def make_new_post(self, photo: bytes, desc: str = '',
                      alt: str = '', geo: bool = False, tag: str = '',
                      location: dict = '') -> bool:
        '''
        Make new post
        '''

        return self._status_check_(
            self.ses.post(self.domain+'create/configure/', data={
                'upload_id': self._upload_photo_(photo),
                'caption': desc,
                'usertags': tag,
                'custom_accessibility_caption': alt,
                'retry_timeout': ''
            }, headers=self._working_headers_()).json()
        )

    def user_info(self, user: str) -> dict:
        '''
        Function return info about user. Searching by username.
        '''

        user = self.domain+user+'/?__a=1'

        try:
            return self.ses.get(user).json()['graphql']['user']
        except Exception:
            return {}

    def user_info_v2(self, user: str) -> dict:
        '''
        More info about user. Paste only username.
        '''

        headers = self._working_headers_().copy()
        headers.update({
            'User-Agent': 'Instagram 10.26.0 Android (18/4.3; 320dpi;' +
            ' 720x1280; Maizu; AFZ 10; armani; qcom; en_US)'
        })

        url = f'https://i.instagram.com/api/v1/users/{user}/usernameinfo/'
        return self.ses.get(url, headers=headers).json()['user']

    def user_activity(self) -> dict:
        '''
        Return info about follow requests, incoming likes
        '''
        return self.ses.get(
            self.domain+'accounts/activity/?__a=1'
        ).json()['graphql']['user']

    def media_info(self, media: str) -> dict:
        '''
        This function return info about media by short code. Example:\n
        https://www.instagram.com/p/B1Zpuv3jnbz - url\n
        You need paste: self.media_info('B1Zpuv3jnbz')
        '''

        media = self.domain+'p/'+media

        try:
            return self.ses.get(media+'/?__a=1').json()['graphql']
        except Exception:
            return {}

    def login(self, user: str, passw: str) -> bool:
        answer = self.ses.post(self.domain+'accounts/login/ajax/', data={
            'username': user,
            'password': passw,
            'queryParams': '{"source":"auth_switcher"}',
            'optIntoOneTap': 'true'
        }, headers=self._working_headers_()).json()

        if not answer['user']:
            print('No user exists with this login.')

        self._loggen_in = answer['authenticated']

        return answer['authenticated']

    def register(self, phoem: str, name: str, user: str, passw: str) -> bool:
        answer = self.ses.post(self.domain+'accounts/web_create_ajax/', data={
            'email': phoem,
            'password': passw,
            'username': user,
            'first_name': name,
            'seamless_login_enabled': '1',
            'tos_version': 'row',
            'opt_into_one_tap': 'false'
        }, headers=self._working_headers_()).json()

        if not answer['account_created']:
            print('Error in progress:', answer['error_type'])

        self._loggen_in = answer['account_created']

        return answer['account_created']

    def search(self, searching: str, what: str = 'users') -> list:
        '''
        searching: write username or hashtag or place name\n
        what: select type what you search ['users', 'places', 'hashtags']
        '''

        if self._action_check_(what, ['users', 'places', 'hashtags']):
            return False

        url = self.domain + 'web/search/topsearch/?context=blended&query=' + \
            searching + '&rank_token=0.5355460316857271&include_reel=true'
        answer = self.ses.get(url).json()

        return answer[what]

    def start_chat(self, to: list) -> dict:
        '''
        to: paste array of username/ID for creating conversation\n
        That\'s for function send_message. I add this in next update.
        '''
        users = [self._check_user_(str(x)) for x in to]
        return self.ses.post(
            self.domain+'direct_v2/web/create_group_thread/', data={
                'recipient_users': str(users)
            }, headers=self._working_headers_()
        ).json()

    def user_action(self, user: str, action: str) -> bool:
        '''
        user: Paste ID or username\n
        action: follow/unfollow, block/unblock
        '''

        if self._action_check_(action, ['follow', 'unfollow']):
            return False

        user = self._check_user_(user)

        if not user:
            return False

        return self._status_check_(self.ses.post(
            self.domain+f'web/friendships/{user}/{action}/',
            headers=self._working_headers_()
        ).json())

    def photo_action(self, photo: str, action: str) -> bool:
        '''
        photo: Paste ID or media short code\n
        action: like or unlike
        '''

        if self._action_check_(action, ['like', 'unlike']):
            return False

        photo = self._check_post_(photo)

        if not photo:
            return False

        url = self.domain+f'web/likes/{photo}/{action}/'

        return self._status_check_(self.ses.post(
            url, data={}, headers=self._working_headers_()
        ).json())

    def media_action(self, photo: str, action: str) -> bool:
        '''
        photo: Paste ID or media short code\n
        action: save or unsave
        '''

        if self._action_check_(action, ['save', 'unsave']):
            return False

        photo = self._check_post_(photo)

        if not photo:
            return False

        url = self.domain+f'web/save/{photo}/{action}/'

        return self._status_check_(self.ses.post(
            url, data={}, headers=self._working_headers_()
        ).json())

    def comment(self, what: str, text: str) -> bool:
        '''
        Comment post by ID or media short code.
        '''
        what = self._check_post_(what)

        if not what:
            return False

        url = self.domain+f'web/comments/{what}/add/'

        return self._status_check_(self.ses.post(url, data={
            'comment_text': text,
            'replied_to_comment_id': ''
        }, headers=self._working_headers_()).json())

    def del_photo(self, photo: str) -> bool:
        '''
        Delete photo by ID or media short code.
        '''
        photo = self._check_post_(photo)

        if not photo:
            return False

        url = self.domain+f'create/{photo}/delete/'
        return self._status_check_(self.ses.post(
            url, data={}, headers=self._working_headers_()
        ).json())
