from typing import List
from pydantic import BaseModel, Field, ConfigDict


class RoadmapResource(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: str = Field(..., description="Resource type: course, docs, book, tutorial")
    title: str = Field(..., description="Title of course, book, or documentation")
    url: str = Field(..., description="Direct link or URL to resource")


class PrioritySkillRoadmap(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    skill: str = Field(..., description="Target skill name")
    why_it_matters: str = Field(..., description="1-2 sentences explaining why this skill matters for this role and seniority")
    resources: List[RoadmapResource] = Field(default_factory=list, description="Curated courses, docs, or books")
    project_task: str = Field(..., description="Small, concrete project or extension to existing candidate project")
    estimated_effort: str = Field(..., description="Estimated effort e.g. '2 weeks, 5–7 hours/week'")
    success_criteria: List[str] = Field(default_factory=list, description="2-4 bullet points describing measurable progress")


class LearningRoadmapContent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    priority_skills: List[PrioritySkillRoadmap] = Field(default_factory=list)
    suggested_sequence: List[str] = Field(default_factory=list)
    general_advice: List[str] = Field(default_factory=list)


class PersonalizedRoadmapResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_key: str
    display_name: str
    learning_roadmap: LearningRoadmapContent
