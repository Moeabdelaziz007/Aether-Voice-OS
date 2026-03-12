from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class NegotiationMessage(BaseModel):
    """Single message in handover negotiation."""
    message_id: str = Field(default_factory=lambda: f"neg-{datetime.now().timestamp()}")
    from_agent: str = Field(description="Sender agent")
    to_agent: str = Field(description="Recipient agent")
    message_type: str = Field(description="offer, counter, accept, reject, clarify")
    content: str = Field(description="Message content")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    attachments: Dict[str, Any] = Field(default_factory=dict)

class HandoverNegotiation(BaseModel):
    """Bidirectional negotiation for handover terms."""
    negotiation_id: str = Field(default_factory=lambda: f"neg-{datetime.now().timestamp()}")
    handover_id: str = Field(description="Reference to parent handover")
    status: str = Field(default="open")
    initiating_agent: str = Field(description="Agent starting the negotiation")
    receiving_agent: str = Field(description="Agent receiving the offer")
    messages: List[NegotiationMessage] = Field(default_factory=list)
    proposed_scope: str = Field(default="")
    proposed_deadline: Optional[str] = None
    proposed_deliverables: List[str] = Field(default_factory=list)
    counter_scope: Optional[str] = None
    counter_deadline: Optional[str] = None
    counter_deliverables: Optional[List[str]] = None
    agreed_scope: Optional[str] = None
    agreed_deadline: Optional[str] = None
    agreed_deliverables: Optional[List[str]] = None
    resolution_timestamp: Optional[str] = None

    def send_message(self, from_agent: str, to_agent: str, message_type: str, content: str, attachments: Optional[Dict[str, Any]] = None) -> NegotiationMessage:
        msg = NegotiationMessage(from_agent=from_agent, to_agent=to_agent, message_type=message_type, content=content, attachments=attachments or {})
        self.messages.append(msg)
        if message_type in ("offer", "counter"): self.status = "negotiating"
        elif message_type == "accept":
            self.status = "accepted"
            self.resolution_timestamp = datetime.now().isoformat()
        elif message_type == "reject":
            self.status = "rejected"
            self.resolution_timestamp = datetime.now().isoformat()
        return msg

    def propose_terms(self, scope: str, deliverables: List[str], deadline: Optional[str] = None) -> NegotiationMessage:
        self.proposed_scope = scope
        self.proposed_deliverables = deliverables
        self.proposed_deadline = deadline
        return self.send_message(from_agent=self.initiating_agent, to_agent=self.receiving_agent, message_type="offer", content=f"Proposed scope: {scope}", attachments={"deliverables": deliverables, "deadline": deadline})

    def accept_terms(self) -> NegotiationMessage:
        scope = self.counter_scope or self.proposed_scope
        deadline = self.counter_deadline or self.proposed_deadline
        deliverables = self.counter_deliverables or self.proposed_deliverables
        self.agreed_scope = scope
        self.agreed_deadline = deadline
        self.agreed_deliverables = deliverables
        return self.send_message(from_agent=self.receiving_agent, to_agent=self.initiating_agent, message_type="accept", content="Terms accepted", attachments={"scope": scope, "deadline": deadline, "deliverables": deliverables})
