import logging
from typing import List, Dict
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Azure OpenAI settings loaded from environment variables
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini")
API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

class AIGenerator:
    def __init__(self):
        if ENDPOINT is None:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set.")
        self.client = AzureOpenAI(
            api_key=API_KEY,
            azure_endpoint=ENDPOINT,
            api_version=API_VERSION
        )
        self.deployment_name = DEPLOYMENT_NAME
        self.logger = logging.getLogger(__name__)

    def _generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.0001) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are an assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content
            return content.strip() if content is not None else ""
        except Exception as e:
            self.logger.error(f"Azure OpenAI error: {str(e)}")
            return "[Error: Could not generate content with Azure OpenAI.]"

    def generate_executive_summary(self, client_name: str, industry: str, service_type: str, similar_content: str) -> str:
        prompt = (
            f"You are an expert business proposal writer. Using the provided examples of past winning proposals (including their structure, pricing, and timelines), generate a new executive summary for the following client and service.\n"
            f"Client Name: {client_name}\nIndustry: {industry}\nService Type: {service_type}\n\n"
            f"Reference the following similar proposal content for structure, style, and detail (if relevant):\n{similar_content}\n\n"
            "- Follow the structure and level of detail shown in the examples.\n"
            "- Use realistic, phase-based context and avoid inventing details not supported by the examples.\n"
            "- The summary should highlight the client's needs, the value our services provide, and set a positive, confident tone. Limit to 2 paragraphs."
        )
        return self._generate(prompt, max_tokens=250, temperature=0.0001)

    def generate_scope_of_work(self, service_type: str, client_name: str, similar_content: str) -> str:
        prompt = (
            f"You are an expert business proposal writer. Using the provided examples of past winning proposals (including their structure, pricing, and timelines), generate a new Scope of Work for the following client and service.\n"
            f"Client Name: {client_name}\nService Type: {service_type}\n\n"
            f"Reference the following similar proposals for structure, phases, deliverables, and timing (if relevant):\n{similar_content}\n\n"
            "- List the key deliverables, project phases, and responsibilities.\n"
            "- Use clear bullet points or short paragraphs.\n"
            "- Use realistic, phase-based timing and deliverables, referencing the patterns in the provided samples.\n"
            "- Do not invent numbers or durations; base all estimates on the context of similar proposals.\n"
            "- If no direct match is found, extrapolate conservatively from the closest example."
        )
        return self._generate(prompt, max_tokens=350, temperature=0.0001)

    def generate_pricing_section(self, service_type: str, client_name: str, similar_content: str) -> str:
        prompt = (
            f"You are an expert business proposal writer. Using the provided examples of past winning proposals (including their pricing tables and models), generate a new Pricing section for the following client and service.\n"
            f"Client Name: {client_name}\nService Type: {service_type}\n\n"
            f"Reference the following similar proposals for pricing structure, numbers, and rationale (if relevant):\n{similar_content}\n\n"
            "- Include a realistic, phase-based pricing table or structure, with actual numbers if available in the examples.\n"
            "- Add a short note about the value and flexibility of the pricing.\n"
            "- Do not invent prices or models; base all estimates on the context of similar proposals.\n"
            "- If no direct match is found, extrapolate conservatively from the closest example."
        )
        return self._generate(prompt, max_tokens=300, temperature=0.0001)

    def generate_full_proposal(self, client_name: str, industry: str, service_type: str, similar_proposals: List[Dict], additional_requirements: str = "") -> Dict[str, str]:
        similar_content = "\n\n---\n\n".join([p.get("text", "") for p in similar_proposals])
        prompt = f"""
You are an expert business proposal writer. Below are examples of past winning proposals, including their structure, pricing, and timelines.

EXAMPLES OF PAST WINNING PROPOSALS:
{similar_content}

---

Now, generate a new proposal for the following client and service:
Client Name: {client_name}
Industry: {industry}
Service Type: {service_type}
Additional Requirements: {additional_requirements}

Instructions:
- Follow the structure and level of detail shown in the examples.
- Use realistic, phase-based pricing and timelines, referencing the patterns in the provided samples.
- Output the proposal in three sections: Executive Summary, Scope of Work (with phases, deliverables, and timing), and Pricing (with a table and total estimate).
- Do not include generic statements or placeholders—be as specific as the examples.
Generate the new proposal below:
"""
        response = self._generate(prompt, max_tokens=1800, temperature=0.0001)
        import re
        sections = {"executive_summary": "", "scope_of_work": "", "pricing": ""}
        exec_match = re.search(r"Executive Summary(.*?)(Scope of Work|$)", response, re.DOTALL | re.IGNORECASE)
        scope_match = re.search(r"Scope of Work(.*?)(Pricing|$)", response, re.DOTALL | re.IGNORECASE)
        pricing_match = re.search(r"Pricing(.*)", response, re.DOTALL | re.IGNORECASE)
        if exec_match:
            sections["executive_summary"] = exec_match.group(1).strip()
        if scope_match:
            sections["scope_of_work"] = scope_match.group(1).strip()
        if pricing_match:
            sections["pricing"] = pricing_match.group(1).strip()
        return sections

    def generate_draft_from_template(self, client_name: str, industry: str, service_type: str, project_goal: str, solution: str, phases: list, pricing: list, total: str, timeline: str) -> Dict[str, str]:
        with open('sample_data/template_proposal.txt', 'r', encoding='utf-8') as f:
            template = f.read()
        draft = template.replace('[Client Name]', client_name)
        draft = draft.replace('[Industry]', industry)
        draft = draft.replace('[Service Type]', service_type)
        draft = draft.replace('[project goal/initiative]', project_goal)
        draft = draft.replace('[service type]', service_type)
        draft = draft.replace('[solution/approach]', solution)
        for i, phase in enumerate(phases, 1):
            draft = draft.replace(f'Phase {i}: [Phase Name] (Weeks X-Y)\n- [Key activities/deliverables]\n- Deliverable: [Deliverable Name]',
                                  f'Phase {i}: {phase["name"]} ({phase["weeks"]})\n- ' + '\n- '.join(phase["activities"]) + f'\n- Deliverable: {phase["deliverable"]}')
            draft = draft.replace(f'| Phase {i}: [Phase Name]            | Fixed Price          | $X,000      | X weeks, includes [description]                                  |',
                                  f'| Phase {i}: {phase["name"]}            | Fixed Price          | {phase["price"]}      | {phase["weeks"]}, includes {phase["description"]}                                  |')
        draft = draft.replace('$XX,000', total)
        draft = draft.replace('X weeks (X months)', timeline)
        import re
        sections = {"executive_summary": "", "scope_of_work": "", "pricing": ""}
        exec_match = re.search(r"Executive Summary(.*?)(Scope of Work|$)", draft, re.DOTALL | re.IGNORECASE)
        scope_match = re.search(r"Scope of Work(.*?)(Pricing|$)", draft, re.DOTALL | re.IGNORECASE)
        pricing_match = re.search(r"Pricing(.*)", draft, re.DOTALL | re.IGNORECASE)
        if exec_match:
            sections["executive_summary"] = exec_match.group(1).strip()
        if scope_match:
            sections["scope_of_work"] = scope_match.group(1).strip()
        if pricing_match:
            sections["pricing"] = pricing_match.group(1).strip()
        return sections

    def generate_full_contract(self, party_a: str, party_b: str, effective_date: str, similar_contracts: List[Dict], additional_requirements: str = "") -> str:
        similar_content = "\n\n---\n\n".join([c.get("text", "") for c in similar_contracts])
        if similar_content.strip():
            prompt = f"""
You are an expert contract drafter. Below are examples of past contracts, including all standard legal clauses (Parties, Term, Payment, Confidentiality, IP, Termination, Dispute Resolution, etc.).

EXAMPLES OF PAST CONTRACTS:
{similar_content}

---
Now, generate a new contract for the following parties:
Party A: {party_a}
Party B: {party_b}
Effective Date: {effective_date}
Additional Requirements: {additional_requirements}

Instructions:
- Follow the structure and level of detail shown in the examples.
- Ensure all standard legal clauses are included (Parties, Term, Payment, Confidentiality, IP, Termination, Dispute Resolution, etc.).
- Do not invent details not supported by the examples; extrapolate conservatively if needed.
- Output the contract as a single document, clearly structured with headings for each clause.
Generate the new contract below:
"""
            contract = self._generate(prompt, max_tokens=1800, temperature=0.0001)
            return contract
        else:
            return self.generate_contract_from_template(party_a, party_b, effective_date)

    def generate_contract_from_template(self, party_a: str, party_b: str, effective_date: str, term: str = "[Termination Date]", payment_terms: str = "[Describe payment structure]", scope: str = "[Describe the services]", jurisdiction: str = "[Jurisdiction]", extra_clauses: str = "") -> str:
        with open('sample_data/template_contract.txt', 'r', encoding='utf-8') as f:
            template = f.read()
        contract = template.replace('[Party A Name]', party_a)
        contract = contract.replace('[Party B Name]', party_b)
        contract = contract.replace('[Effective Date]', effective_date)
        contract = contract.replace('[Termination Date]', term)
        contract = contract.replace('[Describe payment structure, amounts, due dates, and invoicing requirements.]', payment_terms)
        contract = contract.replace('[Describe the services, deliverables, or obligations of each Party.]', scope)
        contract = contract.replace('[Jurisdiction]', jurisdiction)
        if extra_clauses:
            contract += f"\n\nAdditional Clauses:\n{extra_clauses}"
        return contract