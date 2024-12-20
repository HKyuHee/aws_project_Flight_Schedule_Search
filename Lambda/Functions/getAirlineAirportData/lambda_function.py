import json
import boto3

# DynamoDB 클라이언트 생성
dynamodb = boto3.resource('dynamodb')

# 공항과 항공사 테이블 이름 설정
AIRPORTS_TABLE = 'Airports'
AIRLINES_TABLE = 'Airlines'

# 테이블 참조
airports_table = dynamodb.Table(AIRPORTS_TABLE)
airlines_table = dynamodb.Table(AIRLINES_TABLE)

def lambda_handler(event, context):
    try:
        # 공항 데이터 가져오기
        airport_response = airports_table.scan()
        airports = airport_response['Items']
        
        # 항공사 데이터 가져오기
        airline_response = airlines_table.scan()
        airlines = airline_response['Items']
        
        # 결과를 JSON 형식으로 반환
        return {
            'statusCode': 200,
            'body': json.dumps({
                'airports': airports,
                'airlines': airlines
            })
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps('Internal Server Error')
        }
