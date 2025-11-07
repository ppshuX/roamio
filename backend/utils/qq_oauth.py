"""
QQ OAuth 2.0 工具函数
"""
import urllib.parse
import requests
import json
import secrets
from django.conf import settings
from django.core.cache import cache


def generate_state():
    """
    生成随机state参数（用于CSRF防护）
    
    Returns:
        str: 随机state字符串
    """
    return secrets.token_urlsafe(32)


def get_qq_authorize_url(state=None):
    """
    获取QQ授权URL
    
    Args:
        state: CSRF防护参数，如果未提供则自动生成
    
    Returns:
        str: QQ授权URL
    """
    if state is None:
        state = generate_state()
    
    params = {
        'response_type': 'code',
        'client_id': settings.QQ_APP_ID,
        'redirect_uri': settings.QQ_REDIRECT_URI,
        'state': state,
        'scope': 'get_user_info',  # 需要的权限
    }
    
    url = f"{settings.QQ_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
    return url, state


def get_qq_access_token(code):
    """
    通过授权码获取access_token
    
    Args:
        code: QQ返回的授权码
    
    Returns:
        dict: {
            'access_token': str,
            'expires_in': int,
            'refresh_token': str,
            'error': str,  # 如果出错
            'error_description': str
        }
    """
    params = {
        'grant_type': 'authorization_code',
        'client_id': settings.QQ_APP_ID,
        'client_secret': settings.QQ_APP_KEY,
        'code': code,
        'redirect_uri': settings.QQ_REDIRECT_URI,
    }
    
    try:
        response = requests.get(settings.QQ_ACCESS_TOKEN_URL, params=params, timeout=10)
        
        # QQ返回的是URL编码格式：access_token=xxx&expires_in=7776000&refresh_token=xxx
        result = {}
        for pair in response.text.split('&'):
            if '=' in pair:
                key, value = pair.split('=', 1)
                result[key] = urllib.parse.unquote(value)
        
        if 'access_token' in result:
            return {
                'success': True,
                'access_token': result.get('access_token'),
                'expires_in': int(result.get('expires_in', 0)),
                'refresh_token': result.get('refresh_token'),
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'unknown_error'),
                'error_description': result.get('error_description', '获取access_token失败'),
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'request_error',
            'error_description': str(e),
        }


def get_qq_openid(access_token):
    """
    通过access_token获取openid和unionid
    
    Args:
        access_token: QQ access_token
    
    Returns:
        dict: {
            'openid': str,
            'unionid': str,  # 可能为空
            'error': str,
            'error_description': str
        }
    """
    params = {
        'access_token': access_token,
    }
    
    try:
        response = requests.get(settings.QQ_GET_USER_INFO_URL, params=params, timeout=10)
        
        # QQ返回的是JSONP格式：callback({"client_id":"xxx","openid":"xxx"});
        # 需要提取JSON部分
        text = response.text
        if text.startswith('callback(') and text.endswith(');'):
            json_str = text[9:-2]  # 去掉 'callback(' 和 ');'
            data = json.loads(json_str)
            
            if 'openid' in data:
                return {
                    'success': True,
                    'openid': data.get('openid'),
                    'unionid': data.get('unionid'),  # 可能为空
                    'client_id': data.get('client_id'),
                }
            else:
                return {
                    'success': False,
                    'error': data.get('error', 'unknown_error'),
                    'error_description': data.get('error_description', '获取openid失败'),
                }
        else:
            return {
                'success': False,
                'error': 'invalid_response',
                'error_description': 'QQ返回格式错误',
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'request_error',
            'error_description': str(e),
        }


def get_qq_user_info(access_token, openid):
    """
    获取QQ用户详细信息（昵称、头像等）
    
    Args:
        access_token: QQ access_token
        openid: QQ openid
    
    Returns:
        dict: {
            'nickname': str,
            'figureurl': str,  # 头像URL
            'figureurl_1': str,  # 40x40头像
            'figureurl_2': str,  # 100x100头像
            'gender': str,
            'error': str,
            'error_description': str
        }
    """
    params = {
        'access_token': access_token,
        'oauth_consumer_key': settings.QQ_APP_ID,
        'openid': openid,
    }
    
    try:
        response = requests.get(settings.QQ_GET_USER_DETAIL_URL, params=params, timeout=10)
        data = response.json()
        
        if 'ret' in data and data['ret'] == 0:  # ret=0表示成功
            return {
                'success': True,
                'nickname': data.get('nickname', ''),
                'figureurl': data.get('figureurl', ''),
                'figureurl_1': data.get('figureurl_1', ''),
                'figureurl_2': data.get('figureurl_2', ''),
                'gender': data.get('gender', ''),
            }
        else:
            return {
                'success': False,
                'error': data.get('msg', 'unknown_error'),
                'error_description': '获取用户信息失败',
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': 'request_error',
            'error_description': str(e),
        }


def get_qq_user_info_by_code(code):
    """
    通过授权码完整获取QQ用户信息（一步到位）
    
    Args:
        code: QQ返回的授权码
    
    Returns:
        dict: {
            'success': bool,
            'openid': str,
            'unionid': str,
            'nickname': str,
            'avatar_url': str,
            'access_token': str,
            'error': str,
            'error_description': str
        }
    """
    # 1. 获取access_token
    token_result = get_qq_access_token(code)
    if not token_result.get('success'):
        return token_result
    
    access_token = token_result['access_token']
    
    # 2. 获取openid
    openid_result = get_qq_openid(access_token)
    if not openid_result.get('success'):
        return openid_result
    
    openid = openid_result['openid']
    unionid = openid_result.get('unionid', '')
    
    # 3. 获取用户详细信息
    user_info_result = get_qq_user_info(access_token, openid)
    if not user_info_result.get('success'):
        # 即使获取详细信息失败，openid也可以用来登录
        return {
            'success': True,
            'openid': openid,
            'unionid': unionid,
            'nickname': '',
            'avatar_url': '',
            'access_token': access_token,
        }
    
    # 4. 返回完整信息
    return {
        'success': True,
        'openid': openid,
        'unionid': unionid,
        'nickname': user_info_result.get('nickname', ''),
        'avatar_url': user_info_result.get('figureurl_2', user_info_result.get('figureurl_1', '')),
        'access_token': access_token,
    }

