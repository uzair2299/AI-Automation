"""Antigravity / VS Code IDE extension gateway."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/ide", tags=["Channels - IDE Extension"])


class IDERequest(BaseModel):
    file_path: str
    selected_code: str
    action: str  # e.g., 'code_review', 'explain', 'generate_test', 'generate_iac'


@router.post("/action", summary="Handle IDE inline assistance")
async def ide_action_handler(payload: IDERequest):
    """Processes contextual requests from VS Code or Antigravity IDE extensions."""
    return {
        "status": "success",
        "action": payload.action,
        "suggestions": ["Add type annotations", "Verify error handling in async call"]
    }
