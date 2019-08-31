from classes.basic import InstagramBasic


class InstagramProfile(InstagramBasic):
    def set_privacy(self, private: bool) -> bool:
        answer = self.ses.post(self.domain+'accounts/set_private/', data={
            'is_private': str(private).lower()
        }, headers=self._working_headers_()).json()['status']

        if answer != 'ok':
            return False
        else:
            return True

    def set_visiblity(self, status: bool) -> bool:
        answer = self.ses.post(
            self.domain+'accounts/set_presence_disabled/',
            data={
                'presence_disabled': str(status).lower()
            }, headers=self._working_headers_()
        ).json()['status']

        if answer != 'ok':
            return False
        else:
            return True

    def set_stories_share(self, disable: bool) -> bool:
        answer = self.ses.post(
            self.domain+'users/set_disallow_story_reshare_web/',
            data={
                'disabled': str(int(disable))
            }, headers=self._working_headers_()
        ).json()['status']

        if answer != 'ok':
            return False
        else:
            return True

    def change_password(self, old: str, new: str) -> bool:
        answer = self.ses.post(self.domain+'accounts/password/change/', data={
            'old_password': old,
            'new_password1': new,
            'new_password2': new
        }, headers=self._working_headers_()).json()

        if answer['status'] != 'ok':
            print('Hhmmm. See errors:', answer['message']['errors'])
            return False
        else:
            return True

    def authorized_apps(self) -> str:
        '''
        Return array of authorized apps
        '''

        answer = self.ses.get(
            self.domain+'accounts/manage_access/?__a=1'
        ).json()
        return answer['authorizations']

    def change_profile_pic(self, file: bytes, name: str) -> bool:
        url = self.domain+'accounts/web_change_profile_picture/'
        answer = self.ses.post(url, files={'profile_pic': (name, file)},
                               headers=self._working_headers_())
        print(answer)

    def service_subscribe(self, name: str, action: str) -> bool:
        '''
        You can (un)subscribe to service alerts\n
        Names:\n
           announcement - news by email\n
           reminders - remider emails\n
           tutorial - product emails\n
           research - research emails\n
           sms_reminders - get info by SMS messages\n
        Actions:
           subscribe
           unsubscribe
        '''

        valid_name = [
            'announcement', 'reminders', 'tutorial',
            'research', 'sms_reminders'
        ]

        if name not in valid_name:
            print('Bad name for action!')
            return False
        if action not in ['unsubscribe', 'subscribe']:
            print('Bad action for name!')
            return False

        answer = self.ses.post(
            self.domain+'accounts/emailpreferences/',
            data={
                name: action
            }, headers=self._working_headers_()
        ).json()['status']

        if answer != 'ok':
            return False
        else:
            return True
