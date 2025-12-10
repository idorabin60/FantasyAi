from crewai import Agent, Crew, Process, Task
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, HttpUrl
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel, Field
from crewai_tools import SerperDevTool
from crewai import LLM


class PlayerStatus(BaseModel):
    """Status for the next UCL game + why."""
    status: Literal["will start", "will not start", "might not start"] = Field(
        description="Discrete status label for the player's next Champions League match."
    )
    reason: str = Field(
        description="One concise paragraph explaining the decision (injury, coach quotes, lineup reports, etc.)."
    )
    sources: List[str] = Field(
        default_factory=list,
        description="List of URLs used as evidence."
    )
    as_of: str = Field(
        description="ISO date/time when this status was determined, e.g. '2025-10-03T19:45:00+03:00'."
    )


@CrewBase
class PlayersStatusAnalyzer():
    """PlayersStatusAnalyzer crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def player_status_researcher(self) -> Agent:
        return Agent(
            # type: ignore[index]
            config=self.agents_config['player_status_researcher'],
            tools=[SerperDevTool()]
        )

    @task
    def get_player_status_task(self,) -> Task:
        return Task(
            config=self.tasks_config['get_player_status_task'],
            output_pydantic=PlayerStatus
        )

    @crew
    def crew(self) -> Crew:
        """Creates the PlayersStatusAnalyzer crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            llm=LLM(model="openai/gpt-4o", temperature=0),
            memory=False,        # no memory, no RAG storage
            embedder=None,       # don’t auto-create an embedder
            share_crew=False,    # don’t share runs with CrewAI
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
