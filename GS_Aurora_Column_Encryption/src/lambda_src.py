import boto3
import base64

def encrypt_data(key_id, plaintext):
    # 데이터 암호화
    kms_client = boto3.client('kms')
    response = kms_client.encrypt(KeyId=key_id, Plaintext=plaintext)
    ciphertext = response['CiphertextBlob']
    
    return ciphertext

def decrypt_data(key_id, ciphertext):
    # 데이터 복호화
    kms_client = boto3.client('kms')
    response = kms_client.decrypt(KeyId=key_id, CiphertextBlob=ciphertext)
    plaintext = response['Plaintext']
    
    return plaintext   

def lambda_handler(event, context):
    print(event['event_type'])
    print(event['event_text'])

    # KMS 키 
    key_id = 'f00fc17c-d326-4233-9cb8-8a20791232d2'
    
    # 암호화 및 복호화할 데이터
    event_type = event['event_type']
    event_text = event['event_text']
    result_data = ''

    if event_type == 'enc':
        # 데이터 암호화
        _result_data = encrypt_data(key_id, event_text)
        result_data = base64.b64encode(_result_data)

        print(f'Encrypted Data: {result_data}')
    elif event_type == 'dec':
        _event_text = base64.b64decode(event_text)
        # 데이터 복호화
        result_data = decrypt_data(key_id, _event_text)
        print(f'Decrypted Data: {result_data}')

    return {
        'statusCode': 200,
        'body': result_data
    }