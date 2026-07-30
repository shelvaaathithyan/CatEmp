import httpx
import asyncio
from logger import logger
import config

class PredictionAPIClient:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}
    
    async def post_data(self, client: httpx.AsyncClient, url: str, payload: dict, api_name: str):
        logger.info("=" * 48)
        logger.info(f"Calling {api_name} API...")
        
        try:
            response = await client.post(url, json=payload, headers=self.headers, timeout=10.0)
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Response Time: {response.elapsed.total_seconds()}s")
            logger.info(f"Response Body: {response.text}")
        except httpx.TimeoutException:
            logger.error(f"Error calling {api_name} API: Connection timeout")
        except httpx.RequestError as exc:
            logger.error(f"Error calling {api_name} API: Network failure - {exc}")
        except Exception as e:
            logger.error(f"Error calling {api_name} API: Unexpected exception - {e}")
            
    async def send_telemetry(self, demand_payload: dict, maintenance_payload: dict, utilization_payload: dict, anomaly_payload: dict):
        async with httpx.AsyncClient() as client:
            # We must wait for each response as requested ("Wait for each response. Do not stop execution if one API fails.")
            await self.post_data(client, config.DEMAND_ENDPOINT, demand_payload, "Demand Prediction")
            await self.post_data(client, config.MAINTENANCE_ENDPOINT, maintenance_payload, "Maintenance Prediction")
            await self.post_data(client, config.UTILIZATION_ENDPOINT, utilization_payload, "Utilization Prediction")
            await self.post_data(client, config.ANOMALY_ENDPOINT, anomaly_payload, "Anomaly Prediction")
