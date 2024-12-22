"""
Command-line interface for the LLM Project Summarizer.
"""

import click
import logging
import yaml
from pathlib import Path
from typing import Optional

from .summarizer import ProjectSummarizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simplified format for CLI output
)
logger = logging.getLogger(__name__)

def load_config(config_path: Optional[str]) -> dict:
    """Load configuration from YAML file"""
    if not config_path:
        return {}
    
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.warning(f"Error loading config file: {e}")
        return {}

@click.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--exclude', '-e', multiple=True, help='Exclusion patterns')
@click.option('--config', '-c', type=click.Path(), help='Path to config file')
def main(project_path: str, output: Optional[str], exclude: tuple, config: Optional[str]):
    """Analyze and summarize a code project for LLM consumption."""
    try:
        # Load configuration
        config_data = load_config(config)
        
        # Merge command line exclusions with config exclusions
        exclusions = list(exclude) + config_data.get('exclude', [])
        
        # Initialize summarizer
        summarizer = ProjectSummarizer()
        
        # Process project
        results = summarizer.summarize_project(
            project_path,
            exclusions=exclusions
        )
        
        # Determine output path
        output_file = output or config_data.get('output', 'project_summary.md')
        
        # Write summary
        summarizer.write_summary(project_path, results, output_file)
        click.echo(f"Project summary written to {output_file}")
        
    except Exception as e:
        logger.error(f"Error processing project: {e}")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    main()