import json
from main import lambda_handler
from config import config


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

    # Define stubbed changeset for testing
    stubbed_changeset = """
    File: .gitignore\nChanges:\n@@ -29,4 +29,5 @@ node_modules\n \n .ml/*\n hunchly_data/*\n-prod_analysis_data/*\n\\ No newline at end of file\n+prod_analysis_data/*\n+.aider*\n\nFile: alias_scout/agents/scout.py\nChanges:\n@@ -77,7 +77,7 @@ def __init__(\n         # logger.configure(extra={\"session_id\": self.session.id})\n \n         logger.info(\n-            f\"Currently running Variant: {config.VARIANT} Agent: {config.AGENT}\"\n+            f\"Currently running Variant: {config.VARIANT}\"\n         )\n \n         self.session.subject_data = subject\n\nFile: alias_scout/local_handler.py\nChanges:\n@@ -18,7 +18,6 @@\n from alias_scout.config import ConfigManager\n from alias_scout.main import scout_handler\n from alias_scout.services.session import SessionManager\n-from alias_scout.utils import is_within_timeout_timeframe, to_camel_case\n from alias_scout.services.portal_service import resolve_references\n from alias_scout.services.task import SubjectIndexTaskResult, SubjectIndexTaskService\n \n@@ -32,58 +31,42 @@ def main():\n     # Scout Benchmarking dataset\n     index_list = [\n         # \"0be75615-d4fe-4f3b-b6f1-d8a75f164d03\",\n-        \"a8372539-75fb-435b-ad23-a46f28e07fb4\",\n+        # \"a8372539-75fb-435b-ad23-a46f28e07fb4\",\n         # \"855f6b4e-fac1-4bb8-8c72-d92122499c88\",\n         # \"a22d0651-6730-4979-b680-ae78a65d1584\",\n         # \"5f2b2ba1-2334-4b03-96d3-fa9371d7e93f\",\n         # \"f19ea8f7-5309-4c64-b83c-c70f6d51854a\",\n         # \"71a68fde-62b4-4c5f-9151-edc4ba189010\",\n         # \"f28db8c8-4918-4f75-a82c-071ff3ce4317\",\n         # \"608cde09-892c-4cb6-b5f3-d0852d23c60c\",\n+        \"2f98dfb4-a567-4274-8399-0a664ce3576f\"\n     ]\n \n     for index_id in index_list:\n-        index, module, subject = asyncio.run(\n+        index, module, subject, expert_instruction = asyncio.run(\n             resolve_references(\n                 index_id,\n                 # # # MODULE IDS\n-                \"8ec744d0-1808-4eb2-9cd0-c4e37708db2a\", # Civil Records\n+                # \"8ec744d0-1808-4eb2-9cd0-c4e37708db2a\", # Civil Records\n                 # \"750ea087-c24b-4ebc-be60-59c7c9b41af2\",  # Criminal Records\n                 # \"99674666-833f-43dc-91ae-2dac5ee92b69\", #\n+                \"cc9846b4-c0e3-458c-821d-9d192df6ea7a\",\n                 # # # SUBJECT IDS\n                 # \"ebdee481-81db-4465-b236-18f726188ddc\",  # Daniel Croce\n-                \"acd46014-904e-4473-92ee-7c80b1394fc8\", # Michael Jordan\n+                # \"acd46014-904e-4473-92ee-7c80b1394fc8\", # Michael Jordan\n                 # \"a4c886fa-0421-40f8-b461-04fb5eb999cd\",  # James Smith\n+                \"080c3266-f924-4337-86c9-c85ac2931198\",\n+                # Expert Instruction ID\n+                \"01J6DDT11R87E22X5NBYQT6NTT\" \n             )\n         )\n \n         # SCOUT V2\n \n-        agent = ScoutAgent(index, module, subject)\n+        agent = ScoutAgent(index, module, subject, expert_instruction)\n         # result = asyncio.run(agent.execute_task())\n \n-        dummy_trajectory = [\n-            ScoutTrajectory(\n-                node_name=ScoutSteps.NAVIGATE_TO_SEARCH_PAGE.value,\n-                actions=[\n-                    ActionData(\n-                        tool=\"CLICK\",\n-                        tool_args={\"element_id\": \"C\"},\n-                        environment_observation=None,\n-                    ),\n-                    ActionData(\n-                        tool=\"CLICK\",\n-                        tool_args={\"element_id\": \"G\"},\n-                        environment_observation=None,\n-                    ),\n-                    ActionData(\n-                        tool=\"SELECT\",\n-                        tool_args={\"value\": \"Participant Name\", \"element_id\": \"G\"},\n-                        environment_observation=None,\n-                    ),\n-                ],\n-            )\n-        ]\n+        \n \n         # result = asyncio.run(agent.replay_trajectory(dummy_trajectory))\n         result = asyncio.run(agent.investigate())\n\nFile: alias_scout/repository/expert_instruction.py\nChanges:\n@@ -17,7 +17,7 @@ class ExpertInstructionData(BaseModel):\n class ExpertInstructionRepository:\n     def __init__(self):\n         config = ConfigManager.get_config()\n-        self.base_url = f\"{config.api_base_url}/node/scout/expert-instruction\"\n+        self.base_url = f\"{config.api_base_url}/node/scout/expert-instructions\"\n         self.client = InternalAPIClient(config.api_client_credential_arn)\n \n     async def get_item(self, instruction_id: str) -> ExpertInstructionData:\n\nFile: alias_scout/services/portal_service.py\nChanges:\n@@ -52,7 +52,7 @@ async def resolve_references(\n     else:\n         result_places.append(None)\n \n-    if subject_id is not None:\n+    if expert_instruction_id is not None:\n         tasks.append(expert_instruction_repo.get_item(expert_instruction_id))\n         result_places.append(\"expert_instruction\")\n     else:\n\nFile: task-definition.json\nChanges:\n@@ -9,7 +9,7 @@\n   \"containerDefinitions\": [\n     {\n       \"name\": \"scout\",\n-\"image\": \"442241733980.dkr.ecr.us-east-1.amazonaws.com/alias-scout:287da39\",\n+\"image\": \"442241733980.dkr.ecr.us-east-1.amazonaws.com/alias-scout:ba17a67\",\n       \"essential\": true,\n       \"portMappings\": [\n         {\n@@ -41,7 +41,7 @@\n         },\n         {\n           \"name\": \"VARIANT\",\n-\"value\": \"scout-287da39\"\n+\"value\": \"scout-ba17a67\"\n         },\n         {\n           \"name\": \"PW_TEST_SCREENSHOT_NO_FONTS_READY\",\n\nCommit Messages:\nfix/fixing type and minor fixes to get expert instruction\nMerge branch 'master' into fix/expert-instruction-endpoint-bug\nrefactor: remove unnecessary logging and commented-out dummy trajectory code in ScoutAgent and local_handler 
    """

    # Create a mock context with full_context
    context = MockContext(full_context=stubbed_changeset)

    # Call the lambda_handler function with the mock context

    lambda_handler(event, context)
