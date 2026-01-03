#!/usr/bin/env python3
"""
Creative Brief Generator for Autonomous Kids Shorts
Generates complete creative briefs using Phi-3.5 LLM for autonomous story generation.
Includes character design, world building, 3-act structure, 9-shot breakdown with
camera directions, narration, structured JSON output validation, and content safety checks.
"""

import json
import re
import logging
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Any
from enum import Enum
from datetime import datetime
import hashlib

try:
    import ollama
except ImportError:
    ollama = None

try:
    from pydantic import BaseModel, Field, validator
except ImportError:
    BaseModel = object
    Field = None
    validator = None


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentRating(str, Enum):
    """Age-appropriate content ratings"""
    G = "G"  # General Audiences
    PG = "PG"  # Parental Guidance
    PG_13 = "PG-13"  # Parental Guidance 13+
    NOT_SUITABLE = "NOT_SUITABLE"


class ActType(str, Enum):
    """Three-act story structure"""
    SETUP = "Setup"
    CONFRONTATION = "Confrontation"
    RESOLUTION = "Resolution"


@dataclass
class Character:
    """Character design data class"""
    name: str
    age: int
    description: str
    personality_traits: List[str]
    role: str
    appearance: str
    voice_characteristics: Optional[str] = None
    character_arc: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorldBuilding:
    """World building data class"""
    setting: str
    time_period: str
    location_description: str
    cultural_elements: List[str]
    technology_level: str
    environmental_details: str
    rules_of_world: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CameraDirection:
    """Camera movement and framing"""
    type: str  # e.g., "pan", "zoom", "dolly", "tracking", "static"
    description: str
    duration_seconds: float


@dataclass
class ShotBreakdown:
    """Individual shot in the 9-shot breakdown"""
    shot_number: int
    duration_seconds: float
    scene_description: str
    camera_direction: CameraDirection
    narration: str
    character_actions: List[str]
    visual_elements: List[str]
    transitions: Optional[str] = None
    sound_design: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['camera_direction'] = asdict(self.camera_direction)
        return result


@dataclass
class Act:
    """Three-act structure"""
    act_type: ActType
    title: str
    description: str
    duration_seconds: float
    key_plot_points: List[str]
    emotional_tone: str

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['act_type'] = self.act_type.value
        return result


@dataclass
class ContentSafetyCheck:
    """Content safety validation results"""
    is_safe: bool
    rating: ContentRating
    safety_flags: List[str]
    warnings: List[str]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'is_safe': self.is_safe,
            'rating': self.rating.value,
            'safety_flags': self.safety_flags,
            'warnings': self.warnings,
            'recommendations': self.recommendations
        }


@dataclass
class CreativeBrief:
    """Complete creative brief structure"""
    brief_id: str
    title: str
    synopsis: str
    target_audience_age_range: str
    duration_seconds: int
    characters: List[Character]
    world_building: WorldBuilding
    three_act_structure: List[Act]
    nine_shot_breakdown: List[ShotBreakdown]
    themes: List[str]
    moral_lessons: List[str]
    visual_style: str
    animation_style: str
    music_style: str
    content_safety: ContentSafetyCheck
    generated_at: str
    model_used: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'brief_id': self.brief_id,
            'title': self.title,
            'synopsis': self.synopsis,
            'target_audience_age_range': self.target_audience_age_range,
            'duration_seconds': self.duration_seconds,
            'characters': [c.to_dict() for c in self.characters],
            'world_building': self.world_building.to_dict(),
            'three_act_structure': [a.to_dict() for a in self.three_act_structure],
            'nine_shot_breakdown': [s.to_dict() for s in self.nine_shot_breakdown],
            'themes': self.themes,
            'moral_lessons': self.moral_lessons,
            'visual_style': self.visual_style,
            'animation_style': self.animation_style,
            'music_style': self.music_style,
            'content_safety': self.content_safety.to_dict(),
            'generated_at': self.generated_at,
            'model_used': self.model_used,
            'metadata': self.metadata
        }


class ContentSafetyValidator:
    """Validates content for child-appropriate material"""

    # Content that should never appear in kids content
    FORBIDDEN_KEYWORDS = {
        'violence': ['kill', 'murder', 'stab', 'shoot', 'gun', 'weapon', 'blood', 'death', 'die', 'dead'],
        'adult_content': ['sexual', 'sex', 'adult', 'mature', 'inappropriate', 'vulgar'],
        'substance_abuse': ['drug', 'alcohol', 'smoking', 'drunk', 'addict'],
        'scary': ['horror', 'terrifying', 'nightmare', 'monster', 'evil'],
    }

    # Questionable content that requires review
    CAUTION_KEYWORDS = {
        'mild_conflict': ['fight', 'argue', 'yell', 'angry'],
        'minor_peril': ['danger', 'risk', 'injury', 'hurt', 'scared'],
    }

    # Age-appropriate content indicators
    POSITIVE_KEYWORDS = {
        'educational': ['learn', 'discover', 'explore', 'understand', 'knowledge'],
        'positive_values': ['friendship', 'help', 'kind', 'brave', 'honest', 'share', 'care'],
        'growth': ['grow', 'improve', 'overcome', 'achieve', 'success'],
    }

    @staticmethod
    def validate(brief: CreativeBrief) -> ContentSafetyCheck:
        """Validate creative brief for content safety"""
        safety_flags = []
        warnings = []
        recommendations = []
        rating = ContentRating.G

        # Combine all text content for analysis
        content_to_check = f"""
        {brief.title}
        {brief.synopsis}
        {brief.themes}
        {brief.moral_lessons}
        {brief.visual_style}
        {brief.animation_style}
        " ".join([c.description for c in brief.characters])
        {brief.world_building.location_description}
        " ".join([s.narration for s in brief.nine_shot_breakdown])
        """
        content_lower = content_to_check.lower()

        # Check for forbidden content
        for category, keywords in ContentSafetyValidator.FORBIDDEN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    safety_flags.append(f"{category.upper()}: '{keyword}' detected")
                    rating = ContentRating.NOT_SUITABLE

        # Check for caution content
        caution_count = 0
        for category, keywords in ContentSafetyValidator.CAUTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    warnings.append(f"{category.replace('_', ' ').title()}: '{keyword}' detected")
                    caution_count += 1

        # Determine rating based on caution content
        if rating != ContentRating.NOT_SUITABLE:
            if caution_count > 3:
                rating = ContentRating.PG_13
                recommendations.append("Consider reducing conflict intensity")
            elif caution_count > 1:
                rating = ContentRating.PG
                recommendations.append("Minor parental guidance suggested")
            else:
                rating = ContentRating.G

        # Check for positive content
        positive_count = 0
        for category, keywords in ContentSafetyValidator.POSITIVE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    positive_count += 1

        if positive_count > 5:
            recommendations.append("Strong positive messaging and educational value")

        # Age appropriateness checks
        age_range_lower = int(brief.target_audience_age_range.split('-')[0])
        if age_range_lower < 5 and caution_count > 0:
            recommendations.append("Simplify language and reduce scary elements for younger audiences")

        is_safe = rating != ContentRating.NOT_SUITABLE

        return ContentSafetyCheck(
            is_safe=is_safe,
            rating=rating,
            safety_flags=safety_flags,
            warnings=warnings,
            recommendations=recommendations
        )


class JSONValidator:
    """Validates and repairs JSON output from LLM"""

    @staticmethod
    def validate_and_repair(json_str: str) -> Dict[str, Any]:
        """Attempt to parse JSON, repairing common LLM errors"""
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON decode error: {e}. Attempting repair...")
            
            # Attempt basic repairs
            repaired = json_str
            
            # Fix trailing commas
            repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
            
            # Fix missing quotes around keys
            repaired = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', repaired)
            
            # Try parsing again
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                logger.error("Failed to repair JSON")
                raise


class BriefGenerator:
    """Generates creative briefs using Phi-3.5 LLM"""

    def __init__(self, model: str = "phi3.5", temperature: float = 0.8):
        """
        Initialize the brief generator
        
        Args:
            model: LLM model to use (default: phi3.5)
            temperature: Temperature for generation (0.0-1.0)
        """
        self.model = model
        self.temperature = temperature
        self.client = ollama if ollama else None

    def generate_brief(self, prompt: str) -> CreativeBrief:
        """
        Generate a complete creative brief from a prompt
        
        Args:
            prompt: Story concept or creative direction
            
        Returns:
            CreativeBrief object
        """
        if not self.client:
            raise RuntimeError("Ollama not installed. Install with: pip install ollama")

        logger.info(f"Generating creative brief for: {prompt[:50]}...")

        # Generate main brief content
        brief_content = self._generate_content(prompt, "creative_brief")
        
        # Generate 9-shot breakdown
        shots_content = self._generate_content(
            f"{prompt}\n\nBased on this story concept, create a 9-shot breakdown with detailed camera directions and narration",
            "shots_breakdown"
        )

        # Parse responses
        brief_data = JSONValidator.validate_and_repair(brief_content)
        shots_data = JSONValidator.validate_and_repair(shots_content)

        # Build CreativeBrief object
        brief = self._build_brief_object(brief_data, shots_data)

        # Validate content safety
        brief.content_safety = ContentSafetyValidator.validate(brief)

        logger.info(f"Brief generated successfully with ID: {brief.brief_id}")
        return brief

    def _generate_content(self, prompt: str, content_type: str) -> str:
        """Generate content using Phi-3.5 model"""
        if content_type == "creative_brief":
            system_prompt = """You are an expert creative director for animated children's content. 
Generate a comprehensive creative brief in valid JSON format. Include all required fields."""
            
            user_prompt = f"""Create a detailed creative brief for this story concept:
{prompt}

Return a JSON object with these exact fields:
{{
    "title": "Story title",
    "synopsis": "2-3 sentence summary",
    "target_audience_age_range": "4-8",
    "duration_seconds": 180,
    "characters": [
        {{
            "name": "Character name",
            "age": 7,
            "description": "Physical description",
            "personality_traits": ["trait1", "trait2"],
            "role": "protagonist/antagonist/supporting",
            "appearance": "Detailed appearance",
            "voice_characteristics": "Voice description",
            "character_arc": "Character development"
        }}
    ],
    "world_building": {{
        "setting": "Setting name",
        "time_period": "Time period",
        "location_description": "Detailed description",
        "cultural_elements": ["element1", "element2"],
        "technology_level": "Modern/Fantasy/Sci-Fi/etc",
        "environmental_details": "Details about the environment",
        "rules_of_world": ["rule1", "rule2"]
    }},
    "themes": ["theme1", "theme2"],
    "moral_lessons": ["lesson1", "lesson2"],
    "visual_style": "Detailed visual style description",
    "animation_style": "Animation technique",
    "music_style": "Music and sound style"
}}"""

        else:  # shots_breakdown
            system_prompt = """You are an expert storyboard artist and cinematographer.
Generate a 9-shot breakdown with detailed camera directions in valid JSON format."""
            
            user_prompt = f"""Create a 9-shot breakdown for this story:
{prompt}

Return a JSON object:
{{
    "three_act_structure": [
        {{
            "act_type": "Setup",
            "title": "Act title",
            "description": "Act description",
            "duration_seconds": 60,
            "key_plot_points": ["point1", "point2"],
            "emotional_tone": "tone"
        }}
    ],
    "nine_shot_breakdown": [
        {{
            "shot_number": 1,
            "duration_seconds": 15,
            "scene_description": "Scene description",
            "camera_direction": {{
                "type": "pan/zoom/dolly/tracking/static",
                "description": "Detailed camera movement",
                "duration_seconds": 5
            }},
            "narration": "Narration text",
            "character_actions": ["action1", "action2"],
            "visual_elements": ["element1", "element2"],
            "transitions": "Transition type",
            "sound_design": "Sound effects and ambient"
        }}
    ]
}}"""

        try:
            response = self.client.generate(
                model=self.model,
                prompt=user_prompt,
                system=system_prompt,
                stream=False,
                options={
                    'temperature': self.temperature,
                    'top_p': 0.9,
                    'top_k': 40,
                }
            )
            
            content = response.get('response', '')
            logger.info(f"Generated {content_type} content ({len(content)} chars)")
            return content
            
        except Exception as e:
            logger.error(f"Error generating {content_type}: {e}")
            raise

    def _build_brief_object(self, brief_data: Dict, shots_data: Dict) -> CreativeBrief:
        """Build CreativeBrief object from parsed data"""
        
        # Generate brief ID
        brief_id = self._generate_brief_id(brief_data.get('title', 'untitled'))
        
        # Parse characters
        characters = []
        for char_data in brief_data.get('characters', []):
            characters.append(Character(
                name=char_data.get('name', 'Unknown'),
                age=char_data.get('age', 5),
                description=char_data.get('description', ''),
                personality_traits=char_data.get('personality_traits', []),
                role=char_data.get('role', 'character'),
                appearance=char_data.get('appearance', ''),
                voice_characteristics=char_data.get('voice_characteristics'),
                character_arc=char_data.get('character_arc')
            ))
        
        # Parse world building
        wb_data = brief_data.get('world_building', {})
        world_building = WorldBuilding(
            setting=wb_data.get('setting', 'Unknown'),
            time_period=wb_data.get('time_period', 'Present'),
            location_description=wb_data.get('location_description', ''),
            cultural_elements=wb_data.get('cultural_elements', []),
            technology_level=wb_data.get('technology_level', 'Modern'),
            environmental_details=wb_data.get('environmental_details', ''),
            rules_of_world=wb_data.get('rules_of_world', [])
        )
        
        # Parse three-act structure
        three_act = []
        for act_data in shots_data.get('three_act_structure', []):
            act_type_str = act_data.get('act_type', 'Setup').lower()
            if 'setup' in act_type_str:
                act_type = ActType.SETUP
            elif 'confrontation' in act_type_str:
                act_type = ActType.CONFRONTATION
            else:
                act_type = ActType.RESOLUTION
            
            three_act.append(Act(
                act_type=act_type,
                title=act_data.get('title', ''),
                description=act_data.get('description', ''),
                duration_seconds=act_data.get('duration_seconds', 60),
                key_plot_points=act_data.get('key_plot_points', []),
                emotional_tone=act_data.get('emotional_tone', '')
            ))
        
        # Parse 9-shot breakdown
        shots = []
        for shot_data in shots_data.get('nine_shot_breakdown', [])[:9]:
            cam_data = shot_data.get('camera_direction', {})
            camera_direction = CameraDirection(
                type=cam_data.get('type', 'static'),
                description=cam_data.get('description', ''),
                duration_seconds=cam_data.get('duration_seconds', 5)
            )
            
            shots.append(ShotBreakdown(
                shot_number=shot_data.get('shot_number', len(shots) + 1),
                duration_seconds=shot_data.get('duration_seconds', 20),
                scene_description=shot_data.get('scene_description', ''),
                camera_direction=camera_direction,
                narration=shot_data.get('narration', ''),
                character_actions=shot_data.get('character_actions', []),
                visual_elements=shot_data.get('visual_elements', []),
                transitions=shot_data.get('transitions'),
                sound_design=shot_data.get('sound_design')
            ))
        
        return CreativeBrief(
            brief_id=brief_id,
            title=brief_data.get('title', 'Untitled Story'),
            synopsis=brief_data.get('synopsis', ''),
            target_audience_age_range=brief_data.get('target_audience_age_range', '4-8'),
            duration_seconds=brief_data.get('duration_seconds', 180),
            characters=characters,
            world_building=world_building,
            three_act_structure=three_act if three_act else self._generate_default_acts(),
            nine_shot_breakdown=shots if shots else self._generate_default_shots(),
            themes=brief_data.get('themes', []),
            moral_lessons=brief_data.get('moral_lessons', []),
            visual_style=brief_data.get('visual_style', ''),
            animation_style=brief_data.get('animation_style', ''),
            music_style=brief_data.get('music_style', ''),
            content_safety=ContentSafetyCheck(True, ContentRating.G, [], [], []),
            generated_at=datetime.utcnow().isoformat(),
            model_used=self.model,
            metadata={
                'generator_version': '1.0',
                'generation_timestamp': datetime.utcnow().isoformat(),
                'prompt_length': len(str(brief_data))
            }
        )

    @staticmethod
    def _generate_brief_id(title: str) -> str:
        """Generate unique brief ID from title"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        title_hash = hashlib.md5(title.encode()).hexdigest()[:8]
        return f"brief_{timestamp}_{title_hash}"

    @staticmethod
    def _generate_default_acts() -> List[Act]:
        """Generate default three-act structure"""
        return [
            Act(
                act_type=ActType.SETUP,
                title="Introduction",
                description="Introduce characters and setting",
                duration_seconds=60,
                key_plot_points=["Character introduction", "Setting establishment"],
                emotional_tone="Warm and inviting"
            ),
            Act(
                act_type=ActType.CONFRONTATION,
                title="Challenge",
                description="Main conflict or challenge",
                duration_seconds=60,
                key_plot_points=["Problem appears", "Characters respond"],
                emotional_tone="Engaging and dynamic"
            ),
            Act(
                act_type=ActType.RESOLUTION,
                title="Resolution",
                description="Resolution and learning",
                duration_seconds=60,
                key_plot_points=["Problem solved", "Lesson learned"],
                emotional_tone="Satisfying and uplifting"
            )
        ]

    @staticmethod
    def _generate_default_shots() -> List[ShotBreakdown]:
        """Generate default 9-shot breakdown"""
        shots = []
        for i in range(1, 10):
            shots.append(ShotBreakdown(
                shot_number=i,
                duration_seconds=20,
                scene_description=f"Scene {i}",
                camera_direction=CameraDirection(
                    type="static",
                    description="Static camera",
                    duration_seconds=20
                ),
                narration="",
                character_actions=[],
                visual_elements=[],
                transitions="Cut",
                sound_design="Ambient sound"
            ))
        return shots


def export_brief_to_json(brief: CreativeBrief, filepath: str) -> None:
    """Export creative brief to JSON file"""
    with open(filepath, 'w') as f:
        json.dump(brief.to_dict(), f, indent=2)
    logger.info(f"Brief exported to {filepath}")


def export_brief_to_markdown(brief: CreativeBrief, filepath: str) -> None:
    """Export creative brief to markdown file"""
    md_content = f"""# {brief.title}

## Brief ID
{brief.brief_id}

## Synopsis
{brief.synopsis}

## Target Audience
Ages {brief.target_audience_age_range} | Duration: {brief.duration_seconds} seconds

## Characters

"""
    
    for character in brief.characters:
        md_content += f"""### {character.name}
- **Age**: {character.age}
- **Role**: {character.role}
- **Description**: {character.description}
- **Appearance**: {character.appearance}
- **Personality Traits**: {', '.join(character.personality_traits)}
"""
        if character.voice_characteristics:
            md_content += f"- **Voice**: {character.voice_characteristics}\n"
        if character.character_arc:
            md_content += f"- **Character Arc**: {character.character_arc}\n"
        md_content += "\n"

    md_content += f"""## World Building

- **Setting**: {brief.world_building.setting}
- **Time Period**: {brief.world_building.time_period}
- **Technology Level**: {brief.world_building.technology_level}
- **Description**: {brief.world_building.location_description}
- **Environmental Details**: {brief.world_building.environmental_details}
- **Cultural Elements**: {', '.join(brief.world_building.cultural_elements)}
- **Rules of the World**:
"""
    for rule in brief.world_building.rules_of_world:
        md_content += f"  - {rule}\n"

    md_content += f"""
## Themes & Lessons

**Themes**: {', '.join(brief.themes)}

**Moral Lessons**:
"""
    for lesson in brief.moral_lessons:
        md_content += f"- {lesson}\n"

    md_content += f"""
## Visual & Audio Direction

- **Visual Style**: {brief.visual_style}
- **Animation Style**: {brief.animation_style}
- **Music Style**: {brief.music_style}

## Three-Act Structure

"""
    for act in brief.three_act_structure:
        md_content += f"""### Act {act.act_type} - {act.title}
**Duration**: {act.duration_seconds}s | **Tone**: {act.emotional_tone}

{act.description}

**Key Plot Points**:
"""
        for point in act.key_plot_points:
            md_content += f"- {point}\n"
        md_content += "\n"

    md_content += """## 9-Shot Breakdown

"""
    for shot in brief.nine_shot_breakdown:
        md_content += f"""### Shot {shot.shot_number} ({shot.duration_seconds}s)
**Scene**: {shot.scene_description}

**Camera**: {shot.camera_direction.type.upper()} - {shot.camera_direction.description}

**Narration**:
> {shot.narration}

**Character Actions**:
"""
        for action in shot.character_actions:
            md_content += f"- {action}\n"
        
        md_content += f"""
**Visual Elements**:
"""
        for element in shot.visual_elements:
            md_content += f"- {element}\n"
        
        if shot.sound_design:
            md_content += f"\n**Sound Design**: {shot.sound_design}\n"
        
        if shot.transitions:
            md_content += f"**Transition**: {shot.transitions}\n"
        
        md_content += "\n"

    md_content += f"""## Content Safety Assessment

**Rating**: {brief.content_safety.rating.value}
**Safe for Kids**: {'✓ Yes' if brief.content_safety.is_safe else '✗ No'}

**Safety Flags**:
"""
    if brief.content_safety.safety_flags:
        for flag in brief.content_safety.safety_flags:
            md_content += f"- ⚠️  {flag}\n"
    else:
        md_content += "- No flags detected\n"

    md_content += f"""
**Warnings**:
"""
    if brief.content_safety.warnings:
        for warning in brief.content_safety.warnings:
            md_content += f"- {warning}\n"
    else:
        md_content += "- No warnings\n"

    md_content += f"""
**Recommendations**:
"""
    if brief.content_safety.recommendations:
        for rec in brief.content_safety.recommendations:
            md_content += f"- {rec}\n"

    md_content += f"""
## Metadata

- **Generated At**: {brief.generated_at}
- **Model Used**: {brief.model_used}
"""

    with open(filepath, 'w') as f:
        f.write(md_content)
    logger.info(f"Brief exported to {filepath}")


# Example usage and main function
if __name__ == "__main__":
    import sys
    
    # Example prompts for testing
    example_prompts = [
        "A curious rabbit discovers a magical garden where friendship teaches valuable lessons",
        "A young astronaut learns teamwork while exploring a colorful alien planet",
        "A brave little dragon overcomes its fear of heights to save the day"
    ]
    
    def main():
        """Main function for running brief generation"""
        
        # Check if Ollama is available
        if not ollama:
            print("Error: Ollama is not installed.")
            print("Install with: pip install ollama")
            print("Make sure Ollama is running with Phi-3.5 model.")
            sys.exit(1)
        
        # Get prompt from command line or use default
        prompt = sys.argv[1] if len(sys.argv) > 1 else example_prompts[0]
        
        print(f"\n🎬 Creative Brief Generator")
        print(f"{'='*50}")
        print(f"Prompt: {prompt}\n")
        
        try:
            # Generate brief
            generator = BriefGenerator(model="phi3.5", temperature=0.8)
            brief = generator.generate_brief(prompt)
            
            # Export results
            json_path = f"brief_{brief.brief_id}.json"
            md_path = f"brief_{brief.brief_id}.md"
            
            export_brief_to_json(brief, json_path)
            export_brief_to_markdown(brief, md_path)
            
            # Print summary
            print("\n✅ Creative Brief Generated Successfully!")
            print(f"\nTitle: {brief.title}")
            print(f"Brief ID: {brief.brief_id}")
            print(f"Target Age: {brief.target_audience_age_range}")
            print(f"Duration: {brief.duration_seconds} seconds")
            print(f"Characters: {len(brief.characters)}")
            print(f"Content Rating: {brief.content_safety.rating.value}")
            print(f"\n📁 Outputs:")
            print(f"  - JSON: {json_path}")
            print(f"  - Markdown: {md_path}")
            
            return brief
            
        except Exception as e:
            logger.error(f"Error generating brief: {e}")
            sys.exit(1)
    
    main()
