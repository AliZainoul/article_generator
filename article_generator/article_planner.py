#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Article Planner Module

This module connects to the Article Planner Model API via OpenRouter to generate
an article plan based on the provided title and topic.
"""

import os
import json
import logging
import re

from random import choice
from typing import Dict, Any
from article_generator.config import (
    Config,
    ConfigurationError,
    create_openai_client
)
from article_generator.colored_logging import setup_colored_logging

# Configure colored logging
setup_colored_logging(
    level=logging.INFO,
    format_str='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ArticlePlanner:
    """Class for generating article plans using Article AI via OpenRouter."""

    def __init__(self, provider: str = ""):
        """Initialize the ArticlePlanner with API client.
        
        Args:
            provider: The API provider to use (openrouter/gemini). If not specified,
                     uses the default provider from Config.
        """
        try:
            self.provider = provider or Config.API_PROVIDER
            self.client = create_openai_client(self.provider)
        except ConfigurationError as e:
            logger.error("Configuration error: %s", e)
            raise


    def _create_prompt(self, title: str, topic: str, language: str) -> str:
        """Create a prompt for the Article.
        
        Args:
            title: The title of the article
            topic: The main topic of the article
            
        Returns:
            A formatted prompt string for the AI
        """
        prompt : str = f"""
        Crée un plan détaillé pour un article sur '{topic}' avec le titre '{title}'.
        Le plan doit suivre un déroulé pédagogique précis.
        
        IMPORTANT: 
        
        - L'article doit être EXCLUSIVEMENT centré sur le langage {language}, ses fonctionnalités, et ses applications.
        - Le plan doit OBLIGATOIREMENT inclure:

            1. Une introduction qui présente le sujet et son importance dans le contexte de {language}
            2. Quatre sections principales avec des titres clairs, tous en rapport avec {language}
            3. Pour chaque section principale, 2 à 3 sous-sections et des titres d'exemples
            4. Deux sections additionnelles contenant chacune:
                - Section Cas d'utilisation pratiques
                - Section Exercices avec 3 exercices avec code en ANGLAIS et leurs corrigés (IMPORTANT !)
            7. Une conclusion qui résume les points clés et comparaisons
            8. Les exemples ne doivent pas être similaires, pareil pour les exercices.
            9. Tout mot technique dans le langage {language} et tout exemple de code doit être en anglais,
                et tout le contenu des sections doit être en français.
        
        Format de sortie: JSON structuré avec les clés suivantes:
        - 'introduction': texte de l'introduction
        - 'sections': liste d'objets contenant:
            - 'title': titre de la section
            - 'subsections': liste d'objets avec:
            - 'title': titre de la sous-section
            - 'description': description détaillée du contenu de la sous-section (OBLIGATOIRE)
        - 'exercices': liste d'objets contenant:
            - 'title': titre de l'exercice
            - 'description': description détaillée de l'exercice
            - 'solution': solution de l'exercice
        - 'conclusion': texte de la conclusion
        
        IMPORTANT: Chaque sous-section DOIT avoir un titre ET une description détaillée.
        
        Assure-toi que tout le code {language} soit en anglais.
        Assure-toi que tous les exemples, concepts et explications sont spécifiques au langage {language}.
        """

        return prompt

    def generate_plan(self, title: str, topic: str, language: str) -> Dict[str, Any]:
        """Generate an article plan using Article AI.
        
        Args:
            title: The title of the article
            topic: The main topic of the article
            
        Returns:
            A structured plan for the article with sections and subsections
        
        Raises:
            APIError: If there's an error calling the API
        """
        prompt = self._create_prompt(title, topic, language)

        try:
            logger.info("Generating article plan for: %s", title)
            completion = self.client.chat.completions.create(
                model=choice(Config.ARTICLE_PLANNER_MODELS[self.provider]),
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )

            # Parse the response
            response_content = completion.choices[0].message.content

            # Log the raw response for debugging
            logger.debug(f"Raw API response content: '{response_content}'"
                        if response_content else "Raw API response is empty")

            # Check if response content is empty or whitespace only
            if not response_content or response_content.isspace():
                logger.error("Received empty response from API")
                return self._get_fallback_plan(title)

            try:
                fixed_json = self._fix_json_structure(response_content)
                article_plan = json.loads(fixed_json)
                output_dir = os.path.join(os.path.dirname(__file__), "..", "output")
                os.makedirs(output_dir, exist_ok=True)

                # Create a filename based on the article title
                safe_title = title.replace(" ", "_").lower()[:30]
                output_path = os.path.join(output_dir, f"{safe_title}_plan.json")

                # Write the plan as formatted JSON
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(article_plan, f, indent=2, ensure_ascii=False)

                logger.info("Article plan saved to %s:" ,output_path)
                if not self._validate_json_structure(article_plan):
                    logger.error("Invalid JSON structure in response")
                    return self._get_fallback_plan(title)

                return article_plan

            except json.JSONDecodeError as json_err:
                logger.error("Failed to parse JSON response: %s", json_err)
                logger.error("Response content: %s", response_content)
                return self._get_fallback_plan(title)

        except Exception as e:
            logger.error("Error generating article plan: %s", e)
            return self._get_fallback_plan(title)

    def _get_fallback_plan(self, title: str) -> Dict[str, Any]:
        """Create a fallback plan in case of API failure.
        
        Args:
            title: The title of the article
            
        Returns:
            A basic article plan structure
        """
        logger.warning("Using fallback plan due to API error")
        return {
            "introduction": f"Introduction to {title}",
            "sections": [
                {
                    "title": "Basic Concepts",
                    "subsections": [
                        {
                            "title": "Core Features",
                            "description": "Essential Python features and concepts"
                        }
                    ]
                }
            ],
            "conclusion": f"Key takeaways about {title}"
        }

    def _fix_json_structure(self, json_str: str) -> str:
        # Remove any markdown code block delimiters
        if json_str.startswith('```'):
            start_idx = json_str.find('\n') + 1
            end_idx = json_str.rfind('```')
            if start_idx > 0 and end_idx > start_idx:
                json_str = json_str[start_idx:end_idx].strip()

        # Fix common JSON structural issues
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')

        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
        if open_brackets > close_brackets:
            json_str += ']' * (open_brackets - close_brackets)

        # Fix incomplete properties
        json_str = re.sub(r'"[^"]+"\s*:\s*$', '"":""', json_str)
        json_str = re.sub(r'"[^"]+"\s*:\s*,', '"":"",', json_str)
        json_str = re.sub(r'"[^"]+"\s*:\s*\}', '"":""}', json_str)

        # Remove trailing commas
        json_str = re.sub(r',\s*([}\]])', r'\1', json_str)

        # Remove any content after the final closing brace
        if '}' in json_str:
            json_str = json_str[:json_str.rindex('}')+1]

        return json_str

    def _validate_json_structure(self, data: Dict[str, Any]) -> bool:
        required_keys = {'introduction', 'sections', 'conclusion'}
        if not all(key in data for key in required_keys):
            return False

        if not isinstance(data['sections'], list):
            return False

        for section in data['sections']:
            if not isinstance(section, dict):
                return False
            if 'title' not in section or 'subsections' not in section:
                return False
            if not isinstance(section['subsections'], list):
                return False

            for subsection in section['subsections']:
                if not isinstance(subsection, dict):
                    return False
                if 'title' not in subsection or 'description' not in subsection:
                    return False

        return True


# For backwards compatibility
def generate_article_plan(title: str, topic: str, language: str) -> Dict[str, Any]:
    """Legacy function for generating an article plan using Article AI.
    
    Args:
        title: The title of the article
        topic: The main topic of the article
        
    Returns:
        A structured plan for the article with sections and subsections
    """
    _planner = ArticlePlanner()
    return _planner.generate_plan(title, topic, language)


# # For testing purposes
# if __name__ == "__main__":
#     try:
#         planner = ArticlePlanner()
#         test_plan = planner.generate_plan(
#             "Les bases de la programmation Python", 
#             "Python programming language"
#         )
#         print(json.dumps(test_plan, indent=2, ensure_ascii=False))
#     except json.JSONDecodeError as json_err:
#         logger.error("JSON parsing failed: %s", str(json_err))
#     except ConfigurationError as config_err:
#         logger.error("Configuration error: %s", str(config_err))
