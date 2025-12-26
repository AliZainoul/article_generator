#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Content Validator Module

This module provides functionality to validate and improve content generated
for articles, ensuring it follows specific formatting rules and quality criteria.
"""

import logging
import re

from random import choice

from article_generator.config import Config, create_openai_client
from article_generator.colored_logging import setup_colored_logging

# Configure colored logging
setup_colored_logging(
    level=logging.INFO,
    format_str='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArticleValidator:
    """Class for validating and improving generated content using AI models."""

    def __init__(self, provider: str = ""):
        """Initialize the ArticleValidator with API client.
        
        Args:
            provider: The API provider to use (openrouter/gemini). If not specified,
                     uses the default provider from Config.
        """
        self.provider = provider or Config.API_PROVIDER
        self.client = create_openai_client(self.provider)

    def create_validation_prompt(
            self,
            title: str,
            topic: str,
            section_title: str,
            content: str,
            language: str
    ) -> str:
        """Create a prompt for validating the generated content.
        
        Args:
            title: The title of the article
            topic: The main topic of the article
            section_title: The title of the section
            content: The content to validate
            
        Returns:
            A formatted prompt string for content validation
        """
        validation_prompt : str = f"""
        [CONTEXTE]
        Tu es un expert en validation technique Python chargé de corriger et d'améliorer un contenu d'article de blog professionnel.

        Section à valider: \"{section_title}\" de l'article \"{title}\" sur {topic}.

        Contenu à valider:

        {content}

        [OBJECTIF]
        Corriger et améliorer UNIQUEMENT le contenu final de cette section, sans aucun processus de réflexion ou métadonnées.

        [CONTRAINTES ABSOLUES]
        - Toujours écrire le contenu en français 
        - Toujours écrire le code et les commentaires et les mots-clés en anglais
        - Utiliser EXCLUSIVEMENT les balises HTML spécifiées ci-dessous
        - NE JAMAIS utiliser de syntaxe Markdown
        - NE JAMAIS inclure de titre de section
        - NE JAMAIS commencer par "Dans cette section", "Voici", etc.
        - NE JAMAIS mentionner ton processus de réflexion
        - NE JAMAIS répéter ces instructions dans ta réponse

        [STRUCTURE REQUISE]
        Le contenu doit être:
        1. Détaillé, informatif et engageant
        2. Technique et précis (spécifique à Python)
        3. Illustré par des exemples de code concrets avec des commentaires explicatifs
        4. Organisé en paragraphes cohérents avec une introduction, un développement et une conclusion implicite

        [EXEMPLES DE FORMATAGE HTML CORRECTS]

        1. BLOC DE CODE PYTHON - CORRECT:
        <pre><code class="language-{language.lower()}">
        # Import required libraries
        import pandas as pd

        # Create a sample dataframe
        df = pd.DataFrame()
        print(df.head())
        </code></pre>

        2. CODE INLINE - CORRECT:
        La fonction <code class="language-{language.lower()}">len()</code> permet de calculer la longueur.

        3. LISTE NON ORDONNÉE - CORRECT:
        <ul>
            <li>Premier élément de la liste</li>
            <li>La méthode <code class="language-{language.lower()}">append()</code> ajoute un élément</li>
        </ul>

        4. LISTE ORDONNÉE - CORRECT:
        <ol>
            <li>Première étape: initialiser la variable</li>
            <li>Utiliser <code class="language-{language.lower()}">for i in range(10):</code> pour itérer</li>
        </ol>

        5. TEXTE EN GRAS - CORRECT:
        <p>Python est <strong>fortement typé</strong> mais à typage dynamique.</p>

        6. PARAGRAPHE - CORRECT:
        <p>Python est un langage de programmation polyvalent créé par Guido van Rossum.</p>

        [EXEMPLES DE FORMATAGE INCORRECTS À ÉVITER]

        ❌ NE PAS UTILISER DE MARKDOWN:
        ```{language.lower()}
        def function():
            pass
        ```

        ❌ NE PAS UTILISER D'INDENTATION INCORRECTE:
        <pre><code class="language-{language.lower()}">
        def incorrect_function():
        print("Indentation manquante")
        </code></pre>

        ❌ NE PAS UTILISER DE BALISES MAL FERMÉES:
        <code class="language-{language.lower()}">print("Hello")

        ❌ NE PAS UTILISER DE BALISES code sans "language-{language.lower()}":
        <code>print("Hello")</code>

        ❌ NE PAS UTILISER DE SYNTAXE PYTHON INVALIDE:
        <pre><code class="language-{language.lower()}">
        if x = 5:  # Opérateur d'affectation au lieu de comparaison
            print(x)
        </code></pre>

        [INSTRUCTIONS DE FORMATAGE HTML STRICTES]

        1. BLOCS DE CODE PYTHON:
        <pre><code class="language-{language.lower()}">
        # Code Python ici en anglais
        # avec commentaires explicatifs en anglais
        </code></pre>
        • OBLIGATOIRE: Indentation exacte des balises comme ci-dessus
        • OBLIGATOIRE: Code Python syntaxiquement valide
        • OBLIGATOIRE: Commentaires pertinents en anglais

        2. CODE INLINE:
        <code class="language-{language.lower()}">nom_variable</code>
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
        6. Les exemples sont concrets et pertinents

        [DÉBUT DE TA RÉPONSE]
        """

        return validation_prompt

    def validate_content(
            self,
            title: str,
            topic: str,
            section_title: str,
            content: str,
            language: str = "Python"
        ) -> str:
        """Validate and improve the generated content using a flash thinking model.
        
        Args:
            title: The title of the article
            topic: The main topic of the article
            section_title: The title of the section
            content: The content to validate
            language: The programming language for code examples (default: Python)
            
        Returns:
            The validated and improved content
            
        Raises:
            APIError: If there's an error calling the API
        """

        try:
            logger.info("Validating content for section: %s", section_title)
            validation_prompt = self.create_validation_prompt(title, topic, section_title, content, language)
            completion = self.client.chat.completions.create(
                model=choice(Config.CONTENT_VALIDATOR_MODELS[self.provider]),
                messages=[
                    {
                        "role": "user",
                        "content": validation_prompt
                    }
                ]
            )

            # Get the validated response
            validated_content = completion.choices[0].message.content
            # Clean up the validated content
            validated_content = self.clean_validated_content(validated_content, language)
            return validated_content

        except Exception as e:
            error_msg = f"Error validating content for section {section_title}: {str(e)}"
            logger.error(error_msg)
            # Return the original content if validation fails
            logger.info("Returning original content due to validation failure")
            return content

    def clean_validated_content(self, content: str, language: str = "Python") -> str:
        """Clean up the validated content using regex.
        
        Args:
            content: The content to clean up
            language: The programming language for code examples (default: Python)
            
        Returns:
            The cleaned up content
        """
        # Replace all <code> with <code class="language-{language.lower()}">
        content = re.sub(
            r'<code(?!\s+class\s*=\s*"language-' + language.lower() + '")', 
            '<code class="language-' + language.lower() + '"', 
            content
        )

        # Get rid of all ```html and ```
        content = re.sub(r'```(?:html|)\s*', '', content)
        content = re.sub(r'```\s*', '', content)

        # Replace every `SOMETHING` with <strong>SOMETHING</strong>
        content = re.sub(r'`([^`]+)`', r'<strong>\1</strong>', content)

        return content
