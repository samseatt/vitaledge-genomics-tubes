import httpx
import json
from app.core.config import config  # Import the instantiated Config
from app.utils.logging import logger

class VectorDBService:
    """
    Handles interactions with the VectorDB microservice.
    """

    async def populate(self, documents: list):
        """
        Populates the VectorDB with the given documents.
        """
        vectordb_url = f"{config.VECTORDB_URL}/populate/populate"
        headers = {"Content-Type": "application/json"}

        try:
            # Log URL and headers
            # print(f"VectorDB URL: {vectordb_url}")
            # print(f"Headers: {headers}")
            # print("Payload being sent:")
            # print(json.dumps(documents, indent=2))

            async with httpx.AsyncClient() as client:
                # Prepare the request
                request = client.build_request(
                    method="POST",
                    url=vectordb_url,
                    headers=headers,
                    json=documents,
                )

                # Log the full request details
                # print("Prepared request:")
                # print(f"Request method: {request.method}")
                # print(f"Request URL: {request.url}")
                # print(f"Request headers: {request.headers}")
                # print(f"Request content: {request.content.decode()}")

                # Send the request
                response = await client.send(request)
                response.raise_for_status()

                logger.info(f"Wrote to vectorDB with status code: {response.status_code}")
                # logger.debug(f"Response body: {response.text}")

                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise

# import httpx
# from config import config  # Import the instantiated Config

# class VectorDBService:
#     """
#     Handles requests to the VectorDB microservice.
#     """

#     def __init__(self):
#         # Fetch the VECTORDB_URL from config
#         self.VECTORDB_URL = config.VECTORDB_URL  # Ensure VECTORDB_URL is set in the config file

#     async def populate(self, documents: list):
#         """
#         Populates the VectorDB with the given documents.
#         """
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 self.VECTORDB_URL,
#                 json={"documents": documents}
#             )
#             response.raise_for_status()
#             return response.json()



# import httpx

# class VectorDBService:
#     VECTORDB_URL = "http://localhost:8000/populate"

#     async def populate(self, documents: list):
#         """
#         Populates the VectorDB with the given documents.
#         """
#         async with httpx.AsyncClient() as client:
#             response = await client.post(
#                 self.VECTORDB_URL,
#                 json={"documents": documents}
#             )
#             response.raise_for_status()
#             return response.json()
