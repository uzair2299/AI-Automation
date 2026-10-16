"""Agent discovery and metadata catalog API endpoint."""
from fastapi import APIRouter
from smiota.agents.registry import AgentRegistry
from smiota.schemas.agents import AgentMetadataResponse, AgentCapability
from smiota.schemas.common import APIResponse

router = APIRouter(prefix="/agents", tags=["Agent Registry & Discovery"])


@router.get("", response_model=APIResponse[list[AgentMetadataResponse]], summary="List all active AI domain agents")
async def list_registered_agents():
    """Retrieve catalog of all domain agents, operational capabilities, and bound tools."""
    raw_agents = AgentRegistry.list_agents()
    manifests = []
    for a in raw_agents:
        capabilities = [AgentCapability(**c) if isinstance(c, dict) else c for c in a.get("capabilities", [])]
        manifests.append(
            AgentMetadataResponse(
                name=a["name"],
                domain=a.get("domain", a["name"].lower()),
                description=a["description"],
                capabilities=capabilities,
                active=True,
                tools_count=len(a.get("bound_tools", [])),
            )
        )

    return APIResponse(data=manifests, message="Active agents retrieved successfully.")
