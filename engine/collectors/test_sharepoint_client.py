import asyncio
from engine.collectors.sharepoint_client import SharePointClient
from engine.collectors.sharepoint.spo_tenant import SpoTenantDataCollector
from engine.opa_client import opa_client
async def main():
    client = SharePointClient(
        tenant_id="",
        client_id="",
        client_secret="",
        tenant_name="",
        sharepoint_cert_password="",
        sharepoint_cert_path="engine/cert-secret/sharepoint-cert-testing.pfx"
    )

    collector = SpoTenantDataCollector()
    collector_result = await collector.collect(client)

    policy_result = await opa_client.evaluate_policy(
        package_path="cis.microsoft_365_foundations.v6_0_0.control_7_2_2",
        input_data=collector_result,
    )

    print("OPA result:")
    print(policy_result)



if __name__ == "__main__":
    asyncio.run(main())