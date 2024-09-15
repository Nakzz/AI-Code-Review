import json
from lambda_handler import lambda_handler
from config import config
from utils import get_changeset, parse_event_body


class MockContext:
    def __init__(self, full_context):
        self.full_context = full_context


if __name__ == "__main__":
    # Enable test mode
    config.TEST_MODE = True

    # Stub event data for testing
    event = {
        "body": json.dumps(
            {
                "action": "opened",
                "pull_request": {
                    "title": "Sample Pull Request Title",
                    "number": 1,
                    "body": "Sample Pull Request Description",
                    "base": {"ref": "main"},
                    "head": {"ref": "feature-branch"},
                },
                "repository": {"name": "sample-repo", "full_name": "user/sample-repo"},
            }
        )
    }

    # hi = get_changeset("Future-House/paper-qa", "main", "update_retract_test", config.GITHUB_ACCESS_TOKEN)

    # Define stubbed changeset for testing
    stubbed_changeset = """
    File: tests/test_clients.py
Changes:
@@ -17,7 +17,7 @@
 )
 from paperqa.clients.client_models import MetadataPostProcessor, MetadataProvider
 from paperqa.clients.journal_quality import JournalQualityPostProcessor
-from paperqa.clients.retractions import RetrationDataPostProcessor
+from paperqa.clients.retractions import RetractionDataPostProcessor
 
 
 @pytest.mark.vcr
@@ -100,8 +100,9 @@
 @pytest.mark.asyncio
 async def test_title_search(paper_attributes: dict[str, str]) -> None:
     async with aiohttp.ClientSession() as session:
-        client_list = list(ALL_CLIENTS)
-        client_list.remove(RetrationDataPostProcessor)
+        client_list = [
+            client for client in ALL_CLIENTS if client != RetractionDataPostProcessor
+        ]
         client = DocMetadataClient(
             session,
             clients=cast(
@@ -206,8 +207,9 @@ async def test_title_search(paper_attributes: dict[str, str]) -> None:
 @pytest.mark.asyncio
 async def test_doi_search(paper_attributes: dict[str, str]) -> None:
     async with aiohttp.ClientSession() as session:
-        client_list = list(ALL_CLIENTS)
-        client_list.remove(RetrationDataPostProcessor)
+        client_list = [
+            client for client in ALL_CLIENTS if client != RetractionDataPostProcessor
+        ]
         client = DocMetadataClient(
             session,
             clients=cast(
@@ -572,16 +574,20 @@ async def test_ensure_sequential_run_early_stop(
         assert record_indices["early_stop"] != -1, "We should stop early."
 
 
+@pytest.mark.vcr
 @pytest.mark.asyncio
 async def test_crossref_retraction_status():
     async with aiohttp.ClientSession() as session:
+        retract_processor = RetractionDataPostProcessor(
+            "stub_data/stub_retractions.csv"
+        )
         crossref_client = DocMetadataClient(
             session,
             clients=cast(
                 Collection[
                     type[MetadataPostProcessor[Any]] | type[MetadataProvider[Any]]
                 ],
-                [CrossrefProvider, RetrationDataPostProcessor],
+                [CrossrefProvider, retract_processor],
             ),
         )
         crossref_details = await crossref_client.query(

Commit Messages:
updated clients to work with instantiated providers and processors
RetrationDataPostProcessor -> RetractionDataPostProcessor
vcr record_mode removed
    """

    # Create a mock context with full_context
    context = MockContext(full_context=stubbed_changeset)

    # Call the lambda_handler function with the mock context

    lambda_handler(event, context)
  
