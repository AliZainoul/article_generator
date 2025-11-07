#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Article Generator

This script orchestrates the article generation process using two AI models:
- ArticlePlanner: Generates the article outline/plan
- ArticleWriter: Generates detailed content for each section

The generated article is then saved in HTML format using the template.
"""

import sys
import argparse
import logging
from dotenv import load_dotenv

# Import our custom modules
from article_generator.article_planner import ArticlePlanner
from article_generator.article_writer import ArticleWriter
from article_generator.html_generator import HTMLGenerator
from article_generator.colored_logging import setup_colored_logging

# Configure colored logging
setup_colored_logging(
    level=logging.INFO,
    format_str='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def main():
    """Main function to orchestrate the article generation process."""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description="Generate an article using AI"
        )
        parser.add_argument(
            "--title",
            type=str,
            required=True,
            help="Title of the article"
        )
        parser.add_argument(
            "--topic",
            type=str,
            required=True,
            help="Main topic of the article"
        )
        parser.add_argument(
            "--provider",
            type=str,
            choices=["openrouter", "gemini"],
            help="API provider (openrouter/gemini)"
        )
        parser.add_argument(
            "--language",
            type=str,
            required=True,
            help="The programming language for the article"
        )
        args = parser.parse_args()

        logger.info("Generating article: %s\n", args.title)

        logger.info("Step 1: Generating article plan with ArticlePlanner...")
        # Initialize the ArticlePlanner
        try:
            planner = ArticlePlanner(provider=args.provider)
            # Generate article plan using ArticlePlanner
            article_plan = planner.generate_plan(
                args.title,
                args.topic,
                args.language
            )
        except Exception as e:
            logger.error("Error in article plan generation: %s", str(e))
            raise

        logger.info("Step 2: Generating article content with ArticleWriter...")
        # Initialize the ArticleWriter
        try:
            writer = ArticleWriter(provider=args.provider)
            # Generate detailed content for each section using ArticleWriter
            article_content = writer.generate_article_content(
                args.title,
                args.topic,
                article_plan,
                args.language
            )
        except Exception as e:
            logger.error("Error in article content generation: %s", str(e))
            raise

        logger.info("Step 3: Creating HTML article...")
        # Initialize the HTMLGenerator
        try:
            generator = HTMLGenerator()
            # Create HTML article using the template
            filename = generator.create_html_article(args.title, article_content)
        except Exception as e:
            logger.error("Error in HTML generation: %s", str(e))
            raise

        logger.info("Article generated successfully: %s", filename)
        return filename
    except Exception as e:
        logger.error("Article generation failed: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
