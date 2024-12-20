import boto3
import requests
import xml.etree.ElementTree as ET
import json

# 공공데이터포털 API 키
API_KEY = "<실제 오픈API 인증키 입력>"

# DynamoDB 테이블 이름
AIRLINES_TABLE = "Airlines"
AIRPORTS_TABLE = "Airports"

# DynamoDB 리소스 생성
dynamodb = boto3.resource('dynamodb')
airlines_table = dynamodb.Table(AIRLINES_TABLE)
airports_table = dynamodb.Table(AIRPORTS_TABLE)

def fetch_and_store_airlines():
    url = "http://apis.data.go.kr/1613000/DmstcFlightNvgInfoService/getAirmanList"
    params = {'serviceKey': API_KEY, '_type': 'xml'}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        items = root.find('.//items')
        if items is not None:
            for item in items.findall('item'):
                airline_id = item.find('airlineId').text
                airline_name = item.find('airlineNm').text
                
                # 데이터 DynamoDB에 저장
                airlines_table.put_item(Item={
                    'AirlineId': airline_id,
                    'AirlineName': airline_name
                })
            print("Airline data stored successfully!")
        else:
            print("No airline data found.")
    else:
        print(f"Failed to fetch airlines: {response.status_code}")

def fetch_and_store_airports():
    url = "http://apis.data.go.kr/1613000/DmstcFlightNvgInfoService/getArprtList"
    params = {'serviceKey': API_KEY, '_type': 'xml'}
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        items = root.find('.//items')
        if items is not None:
            for item in items.findall('item'):
                airport_id = item.find('airportId').text
                airport_name = item.find('airportNm').text
                
                # 데이터 DynamoDB에 저장
                airports_table.put_item(Item={
                    'AirportId': airport_id,
                    'AirportName': airport_name
                })
            print("Airport data stored successfully!")
        else:
            print("No airport data found.")
    else:
        print(f"Failed to fetch airports: {response.status_code}")

def lambda_handler(event, context):
    try:
        print("Fetching and storing airline data...")
        fetch_and_store_airlines()
        
        print("Fetching and storing airport data...")
        fetch_and_store_airports()
        
        return {
            "statusCode": 200,
            "body": json.dumps("Data successfully fetched and stored in DynamoDB.")
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps(f"An error occurred: {str(e)}")
        }
