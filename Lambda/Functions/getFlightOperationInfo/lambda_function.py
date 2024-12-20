import json
import requests
import xml.etree.ElementTree as ET

# 공공데이터포털 API 키
API_KEY = "<실제 오픈API 인증키 입력>"

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }
    
    try:
        # 쿼리 파라미터 가져오기 (URL에서 직접 파싱)
        query_params = {}
        if 'queryStringParameters' in event and event['queryStringParameters']:
            query_params = event['queryStringParameters']
        elif 'multiValueQueryStringParameters' in event and event['multiValueQueryStringParameters']:
            query_params = {k: v[0] for k, v in event['multiValueQueryStringParameters'].items()}
        
        print("Event:", json.dumps(event))  # 전체 이벤트 출력
        print("Received query parameters:", query_params)
        
        # 필수 파라미터 확인
        required_params = ['depAirportId', 'arrAirportId', 'depPlandTime']
        if not all(param in query_params for param in required_params):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({
                    'error': '필수 파라미터가 누락되었습니다.',
                    'required': required_params,
                    'received': query_params,
                    'event': event  # 디버깅을 위해 전체 이벤트 포함
                }, ensure_ascii=False)
            }

        # API 요청 파라미터 설정
        api_url = 'http://apis.data.go.kr/1613000/DmstcFlightNvgInfoService/getFlightOpratInfoList'
        params = {
            'serviceKey': API_KEY,
            'pageNo': '1',
            'numOfRows': '50',
            '_type': 'xml',
            'depAirportId': query_params['depAirportId'],
            'arrAirportId': query_params['arrAirportId'],
            'depPlandTime': query_params['depPlandTime']
        }
        
        # 선택적 파라미터 추가
        if 'airlineId' in query_params and query_params['airlineId']:
            params['airlineId'] = query_params['airlineId']

        print("API request parameters:", params)

        # API 호출
        response = requests.get(api_url, params=params, timeout=5)
        print("API response status:", response.status_code)
        print("API response content:", response.text)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            items = root.find('.//items')
            result = []
            
            if items is not None:
                for item in items:
                    flight_info = {
                        'airlineNm': item.findtext('airlineNm', 'N/A'),
                        'depAirportNm': item.findtext('depAirportNm', 'N/A'),
                        'arrAirportNm': item.findtext('arrAirportNm', 'N/A'),
                        'depPlandTime': item.findtext('depPlandTime', 'N/A'),
                        'arrPlandTime': item.findtext('arrPlandTime', 'N/A'),
                        'economyCharge': item.findtext('economyCharge', 'N/A'),
                        'prestigeCharge': item.findtext('prestigeCharge', 'N/A'),
                        'vihicleId': item.findtext('vihicleId', 'N/A')
                    }
                    result.append(flight_info)

            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(result if result else {
                    'message': '검색 결과가 없습니다.',
                    'params': params
                }, ensure_ascii=False)
            }
        else:
            return {
                'statusCode': response.status_code,
                'headers': headers,
                'body': json.dumps({
                    'error': 'API 호출 실패',
                    'status': response.status_code,
                    'params': params
                }, ensure_ascii=False)
            }
            
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                'error': str(e),
                'event': event
            }, ensure_ascii=False)
        }