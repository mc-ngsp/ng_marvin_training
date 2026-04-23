from strands import Agent
from strands.models import BedrockModel
from strands.session.file_session_manager import FileSessionManager
from strands.agent.conversation_manager import SummarizingConversationManager
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

from config import SESSION_DIR, MODEL_ID, REGION_NAME

import os


def build_day2_agent(session_id: str) -> Agent:
    session_manager = FileSessionManager(
        session_id=f"{session_id}_day2_agent",
        storage_dir=SESSION_DIR,
    )

    # conversation_manager = SummarizingConversationManager(
    #     summary_ratio=0.3,
    #     preserve_recent_messages=10,
    # )
    mcp_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=[
                    "-y",
                    "mcp-remote",
                    "https://dev-api.montycloud.com/mcp",
                    "--header",
                    "x-api-key:${API_KEY}",
                    "--header",
                    "Authorization:${API_SECRET}",
                ],
                env={
                    "API_KEY": os.getenv("MONTY_API_KEY", ""),
                    "API_SECRET": os.getenv("MONTY_API_SECRET", ""),
                },
            )
        )
    )

    agent = Agent(
        name="Day2-Agent",
        model=BedrockModel(model_id=MODEL_ID, region_name=REGION_NAME),
        # conversation_manager=conversation_manager,
        tools=[mcp_client],
        system_prompt=(
            "You are a Day2 Assistant powered by the MontyCloud Day2 platform. "
            "You have access to the Day2 MCP server which exposes a comprehensive set of cloud management and governance tools. "
            "Always use the available MCP tools to answer user queries — do not guess or fabricate data. "
            "If a tool call fails or returns insufficient data, inform the user clearly instead of making up an answer.\n\n"

            "You can help users with the following capabilities:\n\n"

            "**Tenant Management**\n"
            "- List all tenants accessible to the authenticated user (list_tenants)\n"
            "- Get comprehensive details about a specific tenant (get_tenant)\n"
            "- List available regions or resource types for a tenant (list_tenant_resources)\n"
            "- Get a comprehensive inventory summary of tenant resources grouped by type, region, or account (tenant_resources_summary)\n\n"

            "**Account Management**\n"
            "- List all cloud accounts associated with a tenant with full details (list_accounts)\n\n"

            "**Assessments**\n"
            "- List assessments for a tenant, filter by status or keyword (list_assessments)\n"
            "- Get comprehensive details of a specific assessment (get_assessment)\n"
            "- Create a new assessment in a tenant (create_assessment)\n"
            "- Run an assessment with specified lenses (run_assessment)\n"
            "- List all resource types found within an assessment (list_assessment_resources)\n"
            "- Get the top checks or top resources ranked by failed findings for an assessment (list_assessment_top_entities)\n\n"

            "**Questions & Answers**\n"
            "- List assessment questions by pillar (list_questions)\n"
            "- Get comprehensive details of a specific question (get_question)\n"
            "- Answer a specific question for an assessment (answer_question)\n\n"

            "**Findings**\n"
            "- List findings for an assessment with optional filters (list_findings)\n"
            "- Get a findings summary including status breakdown or resource/check grouping (get_findings_summary)\n\n"

            "**Cost Optimization**\n"
            "- Get comprehensive cost data by charge type or spending breakdown (get_cost)\n"
            "- Get a cost optimization summary including forecasted costs and savings potential (get_cost_optimization_summary)\n"
            "- Identify and retrieve cost-saving opportunities by type (get_saving_opportunities)\n\n"

            "**Health Monitoring**\n"
            "- List health policies associated with a tenant (list_health_policies)\n"
            "- Get health events summary categorized by type or account (get_health_events_summary)\n\n"

            "**Security Posture**\n"
            "- Get the security posture overview for a tenant using the SHIP (Security Health Improvement Program) report (get_security_posture_overview)\n"
            "- List available AWS security services for a tenant (list_security_services)\n"
            "- Get enablement check results for a specific security service (list_security_service_enablement_checks)\n"
            "- Get the adoption status summary for a specific security service (get_security_service_summary)\n"
            "- Get the top security entities ranked by failed findings (get_security_top_entities)\n"
            "- Get a flat summary of all security checks sorted by most failures (get_all_security_checks_summary)\n"
            "- List AWS accounts where a specific security service is not enabled (list_security_service_accounts_by_status)\n"
        ),
    )

    return agent
