# Instagram-API
Simple Instagram API based on web-version

# Example of usage
```python
from ig-web-api import Instagram

a = Instagram()
a.login('USER', 'PASSWORD')

# Get more info about user
print(a.user_info_v2('natgeo'))

# Change profile picture
with open('1.png', 'rb') as f:
    print(a.make_new_post(f.read(), 'That\'s, me!'))

# Some another actions
print('Follow natgeo:', a.user_action('natgeo', 'follow'))
print('Saved photo:', a.media_action('B11rEsiHoQp', 'save'))
print('Liked photo:', a.photo_action('B11rEsiHoQp', 'like'))

```