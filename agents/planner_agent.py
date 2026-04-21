# agents/planner_agent.py
"""
Planner agent for SAFE-INTERN.

Responsibilities:
- Decide which analysis agents should run
- Execute selected agents deterministically
- Return structured agent outputs (NO scoring here)
"""

from typing import Dict, Any, List

from agents import company_agent
from agents import payment_agent
from agents import behavior_agent
from agents import ml_agent


def decide_agents(intake_data: Dict[str, Any]) -> List[str]:
    agents_to_run = ["company", "behavior", "ml"]

    if intake_data.get("payment_mentions"):
        agents_to_run.append("payment")

    return agents_to_run


def run_planner(intake_schema) -> Dict[str, Any]:
    if hasattr(intake_schema, "to_dict"):
        intake_data = intake_schema.to_dict()
    elif hasattr(intake_schema, "dict"):
        intake_data = intake_schema.dict()
    else:
        intake_data = intake_schema

    selected_agents = decide_agents(intake_data)
    results: Dict[str, Any] = {}

    if "company" in selected_agents:
        results["company"] = company_agent.run_company_agent(intake_data)

    if "payment" in selected_agents:
        results["payment"] = payment_agent.run_payment_agent(intake_data)

    if "behavior" in selected_agents:
        results["behavior"] = behavior_agent.run_behavior_agent(intake_data)

    if "ml" in selected_agents:
        results["ml"] = ml_agent.run_ml_analysis(intake_data)

    return results
