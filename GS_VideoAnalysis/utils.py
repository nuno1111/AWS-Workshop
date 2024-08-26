import re

def sanitize_endpoint_name(name):
    # 알파벳, 숫자, 하이픈만 허용하고 나머지는 제거
    sanitized = re.sub(r'[^a-zA-Z0-9-]', '', name)
    
    # 이름이 하이픈으로 시작하거나 끝나면 제거
    sanitized = sanitized.strip('-')
    
    # 이름이 50자를 초과하면 자르기
    if len(sanitized) > 50:
        sanitized = sanitized[:50]
    
    # 이름이 비어있거나 숫자로 시작하면 접두사 추가
    # if not sanitized or sanitized[0].isdigit():
        # sanitized = 'endpoint-' + sanitized
    
    sanitized = 'endpoint-' + sanitized
    
    return sanitized