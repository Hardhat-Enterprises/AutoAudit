import asyncio
from engine.collectors.sharepoint_client import SharePointClient


async def main():
    client = SharePointClient(
        tenant_id="",
        client_id="",
        client_secret="",
        tenant_name="",
        sharepoint_cert_password="admin",
    )


    await client.get_tenant_settings()



if __name__ == "__main__":
    asyncio.run(main())