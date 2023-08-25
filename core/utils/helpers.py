import requests
from django.conf import settings

def send_sms_message(phone_number, message):
    api_key = settings.SMS_GATEWAY_API_KEY
    sender_id = settings.SMS_SENDER_ID

    url = f"https://portal.paylifesms.com/sms/api?action=send-sms&api_key={api_key}&to={phone_number}&from={sender_id}&sms={message}"
    
    try:
        response = requests.request(method="GET", url=url)
        if response.status_code == 200:
            return {"is_successful":True}
        return {"is_resolved":True, "response":response}
    
    except requests.exceptions.RequestException as e:
        return {"is_rejected":True, "error":f"Request Exception: {e}"}

    except Exception as e:
        return {"is_rejected":True, "error":f"Exception: {e}"}
