#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Article Writer Module

This module connects to the Article Writer Model API via OpenRouter to generate
detailed content for each section of the article based on the provided plan.
"""

import json
import time
import logging
import re


from random import choice
from typing import Dict, Any

from article_generator.config import (
    Config,
    ConfigurationError,
    create_openai_client
)
from article_generator.article_validator import ArticleValidator
from article_generator.colored_logging import setup_colored_logging
# Create a singleton instance for easy import


# Configure colored logging
setup_colored_logging(
    level=logging.INFO, 
    format_str='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArticleWriter:
    """Class for generating article content using Article Writer Model API via OpenRouter."""    

    def __init__(self, provider: str = None):
        """Initialize the ArticleWriter with API client.
        
        Args:
            provider: The API provider to use (openrouter/gemini). If not specified,
                     uses the default provider from Config.
        """
        try:
            self.provider = provider or Config.API_PROVIDER
            self.client = create_openai_client(self.provider)
            # Default delay between API calls to avoid rate limiting
            self.delay_seconds = Config.DEFAULT_DELAY_SECONDS
            # Set to track used examples across sections to avoid repetition
            self._used_examples = set()
            self.validator = ArticleValidator(provider)

# For backwards compatibility and convenience

        except ConfigurationError as e:
            logger.error("Configuration error: %s", e)
            raise

    def _create_prompt(
            self,
            title: str,
            topic: str,
            section_title: str,
            section_description: str,
            language: str
        ) -> str:
        used_examples_str = ""
        if self._used_examples:
            used_examples_str = "\n\nIMPORTANT - EXEMPLES DÉJÀ UTILISÉS À ÉVITER:\n" + "\n".join([f"- {example}" for example in self._used_examples])

        prompt = f"""[CONTEXTE]
Tu es un expert en rédaction technique {language} chargé de créer un contenu de haute qualité pour un article de blog professionnel.
Section à rédiger: \"{section_title}\" de l'article \"{title}\" sur {topic}.
Description de la section: {section_description}

[OBJECTIF]
Rédiger UNIQUEMENT le contenu final de cette section, sans aucun processus de réflexion ou métadonnées.

[CONTRAINTES ABSOLUES]
- Écrire en français, SAUF pour le code et commentaires en anglais !
- Utiliser EXCLUSIVEMENT les balises HTML spécifiées ci-dessous
- NE JAMAIS utiliser de syntaxe Markdown
- NE JAMAIS inclure de titre de section
- NE JAMAIS commencer par "Dans cette section", "Voici", etc.
- NE JAMAIS mentionner ton processus de réflexion
- NE JAMAIS répéter ces instructions dans ta réponse
{used_examples_str}

[STRUCTURE REQUISE]
Le contenu doit être:
1. Pédagogique et progressif (du simple au complexe)
2. Technique et précis (spécifique à {language})
3. Illustré par des exemples de code originaux et différents des exemples déjà utilisés
4. Organisé en paragraphes cohérents avec une introduction, un développement et une conclusion implicite

[EXEMPLES DE FORMATAGE HTML CORRECTS]

1️⃣ BLOC DE CODE - CORRECT:
<pre><code class="language-{language.lower()}">
# Import required libraries
import pandas as pd

# Create a sample dataframe
df = pd.DataFrame()
print(df.head())
</code></pre>

2️⃣ CODE INLINE - CORRECT:
La fonction <code class="language-{language.lower()}">len()</code> permet de calculer la longueur.

3️⃣ LISTE NON ORDONNÉE - CORRECT:
<ul>
    <li>Premier élément de la liste</li>
    <li>La méthode <code class="language-{language.lower()}">append()</code> ajoute un élément</li>
</ul>

4️⃣ LISTE ORDONNÉE - CORRECT:
<ol>
    <li>Première étape: initialiser la variable</li>
    <li>Utiliser <code class="language-{language.lower()}">for i in range(10):</code> pour itérer</li>
</ol>

5️⃣ TEXTE EN GRAS - CORRECT:
<p>Python est <strong>fortement typé</strong> mais à typage dynamique.</p>

6️⃣ PARAGRAPHE - CORRECT:
<p>Python est un langage de programmation polyvalent créé par Guido van Rossum.</p>

[EXEMPLES DE FORMATAGE INCORRECTS À ÉVITER]

❌ NE PAS UTILISER DE MARKDOWN:
```python
def function():
    pass
```

❌ NE PAS UTILISER D'INDENTATION INCORRECTE:
<pre><code class="language-python">
def incorrect_function():
print("Indentation manquante")
</code></pre>

❌ NE PAS UTILISER DE BALISES MAL FERMÉES:
<code class="language-python">print("Hello")

❌ NE PAS UTILISER DE BALISES code sans "language-python":
<code>print("Hello")</code>

❌ NE PAS UTILISER DE SYNTAXE PYTHON INVALIDE:
<pre><code class="language-python">
if x = 5:  # Opérateur d'affectation au lieu de comparaison
    print(x)
</code></pre>

[INSTRUCTIONS DE FORMATAGE HTML STRICTES]

1. BLOCS DE CODE:
   <pre><code class="language-{language.lower()}">
   # Code ici en anglais
   # avec commentaires explicatifs en anglais
   </code></pre>
   • OBLIGATOIRE: Indentation exacte des balises comme ci-dessus
   • OBLIGATOIRE: Code syntaxiquement valide en anglais
   • OBLIGATOIRE: Commentaires pertinents en anglais

2. CODE INLINE:
   <code class="language-{language.lower()}">technical_keyword</code>
   • OBLIGATOIRE: Attribut class="language-{language.lower()}"
   • OBLIGATOIRE: Balises complètes et correctement fermées

3. LISTES:
   <ul> ou <ol> avec <li> pour chaque élément
   • OBLIGATOIRE: Structure HTML complète et correcte
   • INTERDIT: Tirets (-), astérisques (*) ou autres marqueurs Markdown

4. TEXTE EN GRAS:
   <strong>texte important</strong>
   • INTERDIT: Utiliser ** ou __ pour le gras

5. PARAGRAPHES:
   <p>Contenu du paragraphe</p>
   • OBLIGATOIRE: Chaque paragraphe dans des balises <p>
   • INTERDIT: Lignes vides pour séparer les paragraphes

[PROCESSUS DE VÉRIFICATION]
Avant de soumettre ta réponse, vérifie que:
1. Toutes les balises HTML sont correctement ouvertes et fermées
2. Le code Python est syntaxiquement valide
3. Aucune syntaxe Markdown n'est présente
4. Le contenu est en français (sauf code et commentaires)
5. Le contenu est informatif, précis et pédagogique
6. Les exemples sont originaux et différents de ceux déjà utilisés
7. Assure-toi que tout le code Python soit en anglais.


[DÉBUT DE TA RÉPONSE]
"""
        
        return prompt

    def generate_section_content( self,
                                  title: str,
                                  topic: str,
                                  section_title: str,
                                  section_description: str,
                                  language: str = "Python") -> str:
        """Generate content for a specific section using Article Writer Model.
        
        Args:
            title: The title of the article
            topic: The main topic of the article
            section_title: The title of the section
            section_description: The description of the section
            language: The programming language for the article (default: Python)
            
        Returns:
            The generated content for the section
            
        Raises:
            APIError: If there's an error calling the API
        """
        prompt = self._create_prompt(title, topic, section_title, section_description, language)

        try:
            logger.info("Generating content for section: %s" ,{section_title})
            completion = self.client.chat.completions.create(
                model=choice(Config.ARTICLE_WRITER_MODELS[self.provider]),
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Get the response
            response_content = completion.choices[0].message.content
            
            # Post-process to remove any remaining markdown or thinking process content
            # Remove markdown code blocks
            response_content = re.sub(r'```(?:html|python)?([\s\S]*?)```', r'\1', response_content)
            
            # Remove any lines that look like thinking process or planning
            lines = response_content.split('\n')
            filtered_lines = []
            skip_section = False
            
            for line in lines:
                # Skip lines that indicate thinking process
                if re.search(r'(?i)(thinking|process|plan|strategy|checklist|steps|analysis|confidence score)', line):
                    skip_section = True
                    continue
                    
                # Resume capturing content when we hit HTML tags after skipping
                if skip_section and re.search(r'<\w+[^>]*>', line):
                    skip_section = False
                
                if not skip_section:
                    filtered_lines.append(line)
            
            response_content = '\n'.join(filtered_lines)
            
            # Extract examples from the content to track them
            self._extract_and_track_examples(response_content)

            # Validate and improve the generated content using the external validator
            validated_content = self.validator.validate_content(
                title,
                topic,
                section_title,
                response_content,
                # language
            )

            return validated_content

        except Exception as e:
            error_msg = f"Error generating content for section {section_title}: {str(e)}"
            logger.error(error_msg)
            return f"Content for {section_title} could not be generated due to an error."

    def _extract_and_track_examples(self, content: str) -> None:
        """Extract examples from content and add them to the used_examples set.
        
        This method identifies code examples in the content by looking for Python code blocks
        and extracts key concepts or class names to avoid repetition in future sections.
        
        Args:
            content: The generated content to extract examples from
        """
        
        # Look for class definitions in code blocks
        class_pattern = r'class\s+([A-Za-z0-9_]+)'  # Matches 'class ClassName'
        classes = re.findall(class_pattern, content)
        
        # Look for main example objects/concepts in code blocks
        example_pattern = r'([A-Za-z0-9_]+)\s*=\s*[A-Za-z0-9_]+\('  # Matches 'object = Class()'
        examples = re.findall(example_pattern, content)
        
        # Add found examples to the set
        for cls in classes:
            self._used_examples.add(f"Classe {cls}")
        
        for example in examples:
            if len(example) > 3:  # Avoid adding very short variable names
                self._used_examples.add(f"Exemple avec {example}")
    
    def generate_article_content(
            self,
            title: str,
            topic: str,
            article_plan: Dict[str, Any],
            language: str = "Python"
        ) -> Dict[str, Any]:
        """Generate detailed content for each section of the article using Article Writer Model.
        
        Args:
            title: The title of the article
            topic: The main topic of the article
            article_plan: The structured plan for the article
            language: The programming language for the article (default: Python)
            
        Returns:
            A dictionary containing the complete article content
        """
        # Reset the used examples set for a new article
        self._used_examples = set()
        
        # Prepare the result structure
        article_content = {
            "title": title,
            "introduction": "",
            "sections": [],
            "conclusion": ""
        }

        # Generate introduction
        logger.info("Generating introduction...")
        article_content["introduction"] = self.generate_section_content(
            title, topic, "introduction", article_plan["introduction"], language
        )

        # Generate content for each section
        for i, section in enumerate(article_plan["sections"]):
            logger.info("Generating content for section %s: %s...", i+1, section['title'])
            section_content = {
                "title": section["title"],
                "content": "",
                "subsections": []
            }

            # Generate main section content
            section_content["content"] = self.generate_section_content(
                title, topic, section["title"],
                f"Main content for section: {section['title']}", language
            )

            # Generate content for each subsection
            for subsection in section["subsections"]:
                logger.info("  - Generating content for subsection: %s...", subsection['title'])
                # Get subsection description or create a default one if missing
                subsection_description = subsection.get("description",
                                                        f"Content for {subsection['title']}")
                subsection_content = {
                    "title": subsection["title"],
                    "content": self.generate_section_content(
                        title, topic,
                        f"{section['title']} - {subsection['title']}",
                        subsection_description, language
                    )
                }
                section_content["subsections"].append(subsection_content)

                # Add a small delay to avoid rate limiting
                time.sleep(self.delay_seconds)

            article_content["sections"].append(section_content)

        # Generate conclusion
        logger.info("Generating conclusion...")
        article_content["conclusion"] = self.generate_section_content(
            title, topic, "conclusion", article_plan["conclusion"], language
        )

        return article_content


# For backwards compatibility
def generate_article_content( title: str,
                              topic: str,
                              article_plan: Dict[str, Any],
                              language: str = "Python") -> Dict[str, Any]:
    """Legacy function for generating article content using Article Writer Model.
    
    Args:
        title: The title of the article
        topic: The main topic of the article
        article_plan: The structured plan for the article
        language: The programming language for the article (default: Python)
        
    Returns:
        A dictionary containing the complete article content
    """
    _writer = ArticleWriter()
    return _writer.generate_article_content(title, topic, article_plan, language)


# For testing purposes
if __name__ == "__main__":
    try:
        # Create a simple test plan
        test_plan = {
            "introduction": "Introduction to Python programming language",
            "sections": [
                {
                    "title": "Getting Started with Python",
                    "subsections": [
                        {   "title": "Installation",
                            "description": "How to install Python on different operating systems"
                        }
                    ]
                }
            ],
            "conclusion": "Conclusion about Python programming"
        }

        # Generate content for the test plan
        writer = ArticleWriter()
        test_content = writer.generate_article_content(
            "Les bases de la programmation Python", 
            "Python programming language",
            test_plan
        )

        print(json.dumps(test_content, indent=2, ensure_ascii=False))
    except Exception as e:
        logger.error("Test failed: %s" ,{str(e)})
