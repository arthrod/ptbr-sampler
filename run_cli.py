#!/usr/bin/env python
"""
Wrapper script for ptbr_sampler CLI to handle command-line arguments.
This script uses standard typer but calls the async sampling logic using uvloop.
"""
import sys
import os
import asyncio
from pathlib import Path
from typing import Any, Optional
from datetime import timedelta, timezone

# Shut down standard logging to prevent INFO logs from libraries
import logging
logging.getLogger().setLevel(logging.WARNING)
for handler in logging.getLogger().handlers:
    handler.setLevel(logging.WARNING)

import uvloop
import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn
from loguru import logger

# Add the project root to the path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import our async functions and types
from ptbr_sampler.br_name_class import TimePeriod
from ptbr_sampler.sampler import sample as sampler_sample

# Configure logger
logger.remove()  # Remove default handler

# Add stderr logger for console output - filter out DEBUG and INFO messages
logger.add(
    sys.stderr,
    format='<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <blue>{name}:{line}</blue> - <level>{message}</level>',
    filter=lambda record: record['level'].name in ['WARNING', 'ERROR', 'CRITICAL'],
    level='WARNING',  # This makes the handler only process WARNING and above
    backtrace=True,
    diagnose=True,
    colorize=True,
)

# Configure default logger level to WARNING for all modules
logger.configure(handlers=[{"sink": sys.stderr, "level": "WARNING"}])

# Add file logger for persistent logs - includes all messages
logger.add(
    'ptbr_sampler.log',
    rotation='10 MB',
    format='{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} - {message}',
    level='INFO',
    backtrace=True,
    diagnose=True,
)

# Add special detailed log file for all messages including debug
logger.add(
    'ptbr_sampler.log.all',
    rotation='10 MB',
    format='{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}',
    level='DEBUG',
    backtrace=True,
    diagnose=True,
)

# Configure Brasilia timezone (UTC-3)
BRASILIA_TZ = timezone(timedelta(hours=-3))

# Configure logger with Brasilia timezone
logger.configure(extra={'timezone': BRASILIA_TZ})

# Create Typer app
app = typer.Typer(
    help="""
🇧🇷 Brazilian Realistic Data Generator CLI 

Generate statistically accurate Brazilian personal data including:
- Names and surnames historically accurate with period-specific sampling
- Locations with population-weighted distribution
- Valid documents (CPF, RG, PIS, CNPJ, CEI)
- Phone numbers with appropriate area codes

All generated data is based on real demographic information and 
valid document formats. Perfect for testing, data science, and 
application development targeting the Brazilian market.

For complete documentation: https://github.com/username/ptbr-sampler
""", 
    add_completion=False
)
console = Console()

@app.command()
def sample(
    qty: int = typer.Option(1, '--qty', '-q', help='Number of samples to generate'),
    city_only: bool = typer.Option(False, '--city-only', '-c', help='Return only city names'),
    state_abbr_only: bool = typer.Option(False, '--state-abbr-only', '-sa', help='Return only state abbreviations'),
    state_full_only: bool = typer.Option(False, '--state-full-only', '-sf', help='Return only full state names'),
    only_cep: bool = typer.Option(False, '--only-cep', '-oc', help='Return only CEP'),
    cep_without_dash: bool = typer.Option(False, '--cep-without-dash', '-nd', help='Return CEP without dash'),
    make_api_call: bool = typer.Option(False, '--make-api-call', '-mac', help='Make API calls for real CEP data'),
    time_period: TimePeriod = typer.Option(TimePeriod.UNTIL_2010, '--time-period', '-t', help='Time period for name sampling'),
    return_only_name: bool = typer.Option(False, '--return-only-name', '-rn', help='Return only names without location'),
    name_raw: bool = typer.Option(False, '--name-raw', '-r', help='Return names in raw format (all caps)'),
    json_path: Path = typer.Option('ptbr_sampler/data/cities_with_ceps.json', '--json-path', '-j', help='Path to city/state data JSON file'),
    names_path: Path = typer.Option('ptbr_sampler/data/names_data.json', '--names-path', '-np', help='Path to first names data file'),
    middle_names_path: Path = typer.Option('ptbr_sampler/data/middle_names.json', '--middle-names-path', '-mnp', help='Path to middle names data file'),
    only_surname: bool = typer.Option(False, '--only-surname', '-s', help='Return only surnames'),
    top_40: bool = typer.Option(False, '--top-40', '-t40', help='Use only top 40 surnames'),
    with_only_one_surname: bool = typer.Option(False, '--one-surname', '-os', help='Use single surname'),
    always_middle: bool = typer.Option(False, '--always-middle', '-am', help='Always include middle name'),
    only_middle: bool = typer.Option(False, '--only-middle', '-om', help='Return only middle names'),
    always_cpf: bool = typer.Option(True, '--always-cpf', '-ac', help='Always include CPF'),
    always_pis: bool = typer.Option(False, '--always-pis', '-ap', help='Always include PIS'),
    always_cnpj: bool = typer.Option(False, '--always-cnpj', '-acn', help='Always include CNPJ'),
    always_cei: bool = typer.Option(False, '--always-cei', '-ace', help='Always include CEI'),
    always_rg: bool = typer.Option(True, '--always-rg', '-ar', help='Always include RG'),
    always_phone: bool = typer.Option(True, '--always-phone', '-aph', help='Always include phone number'),
    only_cpf: bool = typer.Option(False, '--only-cpf', '-ocpf', help='Return only CPF'),
    only_pis: bool = typer.Option(False, '--only-pis', '-op', help='Return only PIS'),
    only_cnpj: bool = typer.Option(False, '--only-cnpj', '-ocn', help='Return only CNPJ'),
    only_cei: bool = typer.Option(False, '--only-cei', '-oce', help='Return only CEI'),
    only_rg: bool = typer.Option(False, '--only-rg', '-or', help='Return only RG'),
    only_fone: bool = typer.Option(False, '--only-fone', '-of', help='Return only phone number'),
    include_issuer: bool = typer.Option(True, '--include-issuer', '-ii', help='Include issuer in RG'),
    only_document: bool = typer.Option(False, '--only-document', '-od', help='Return only documents'),
    surnames_path: Path = typer.Option('ptbr_sampler/data/surnames_data.json', '--surnames-path', '-sp', help='Path to surnames data file'),
    locations_path: Path = typer.Option('ptbr_sampler/data/locations_data.json', '--locations-path', '-lp', help='Path to locations data file'),
    save_to_jsonl: Optional[str] = typer.Option(None, '--save-to-jsonl', '-sj', help='Save generated samples to a JSONL file'),
    all_data: bool = typer.Option(False, '--all', '-a', help='Include all possible data in the generated samples'),
    batch_size: int = typer.Option(100, '--batch-size', '-bs', help='Number of items to process in each batch (default: 100)'),
    num_workers: int = typer.Option(100, '--workers', '-w', help='Number of workers to use for API calls (default: 100)'),
    easy: Optional[int] = typer.Option(None, '--easy', '-e', help='Easy mode with integer qty'),
    append_to_jsonl: bool = typer.Option(True, '--append', '-ap', help='Append to JSONL file instead of overwriting'),
):
    """Generate random Brazilian samples with comprehensive information.

This command generates statistically accurate Brazilian personal data including names,
locations, and documents. The data is generated based on real demographic information
and follows valid document formats.

[bold]Examples:[/bold]
  # Generate a single complete profile
  $ uv run run_cli.py sample

  # Generate 10 profiles and save to a JSONL file
  $ uv run run_cli.py sample --qty 10 --save-to-jsonl output.jsonl

  # Generate 5 profiles with only CPF documents
  $ uv run run_cli.py sample --qty 5 --only-cpf

  # Quick mode with API calls and all data
  $ uv run run_cli.py sample --easy 20

  # Get only location data for 3 samples
  $ uv run run_cli.py sample --qty 3 --city-only --state-abbr-only

The generated data can be customized using various options for locations,
names, and documents. All data is proportional to the actual population
distribution in Brazil.
    """
    # Install uvloop for async operations
    uvloop.install()

    # Setup coroutine to run
    async def run_sample():
        try:
            # Process easy mode if specified
            if easy is not None:
                console.print(Panel(
                    '[bright_yellow]Modo Fácil Ativado[/bright_yellow]', 
                    title="[bright_green]PTBR Sampler[/bright_green]", 
                    border_style="green"
                ))
                logger.info(f'Easy mode enabled with quantity: {easy}')
                _qty = easy
                _make_api_call = True
                _all_data = True
                _always_phone = True
                _save_to_jsonl = save_to_jsonl if save_to_jsonl else 'output/output.jsonl'

                # Ensure output directory exists
                output_path = Path(_save_to_jsonl)
                if output_path.parent != Path() and not output_path.parent.exists():
                    console.print(f'[yellow]Creating output directory: {output_path.parent}[/yellow]')
                    output_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                _qty = qty
                _make_api_call = make_api_call
                _all_data = all_data
                _always_phone = always_phone
                _save_to_jsonl = save_to_jsonl

            # Show configuration summary
            config_items = []
            
            config_items.append(f"[bright_green]Quantidade:[/bright_green] [bright_yellow]{_qty}[/bright_yellow]")
            config_items.append(f"[bright_green]Chamada de API:[/bright_green] [{'bright_yellow' if _make_api_call else 'dim blue'}]{_make_api_call}[/]")
            config_items.append(f"[bright_green]Todos os dados:[/bright_green] [{'bright_yellow' if _all_data else 'dim blue'}]{_all_data}[/]")
            config_items.append(f"[bright_green]Incluir telefone:[/bright_green] [{'bright_yellow' if _always_phone else 'dim blue'}]{_always_phone}[/]")
            
            if _save_to_jsonl:
                save_mode = '[bright_yellow]append[/]' if append_to_jsonl else '[bright_blue]overwrite[/]'
                config_items.append(f"[bright_green]Salvar em:[/bright_green] [bright_yellow]{_save_to_jsonl}[/] ({save_mode})")
                
            config_items.append(f"[bright_green]Tamanho do lote:[/bright_green] [bright_yellow]{batch_size}[/] amostras")
            config_items.append(f"[bright_green]Trabalhadores:[/bright_green] [bright_yellow]{num_workers}[/] workers")

            config_text = "\n".join(config_items)
            console.print(Panel(
                config_text, 
                title="[bright_green]Configuração do Gerador[/bright_green]",
                border_style="bright_yellow", 
                expand=False
            ))

            # Log batch size and workers configuration
            logger.info(f"Using batch_size={batch_size}, num_workers={num_workers}")
            
            # Calculate total number of batches
            total_batches = (_qty + batch_size - 1) // batch_size
            current_batch = 1

            # Implement a simplified progress display with Brazilian colors (like the example code)
            with Progress() as progress:
                # Add main task with Brazilian colors - simple like the example
                search_task = progress.add_task('[bright_green]Gerando amostras...', total=None)
                
                # Add API task with Brazilian colors
                api_task = None
                if _make_api_call:
                    api_task = progress.add_task("[bright_yellow]Chamadas de API:", visible=False, total=1.0)
                
                # Add batch task with Brazilian colors 
                batch_task = progress.add_task("[bright_green]Lote atual:", visible=False, total=1.0)
                
                # Update progress callback to use Brazilian colors
                async def progress_callback(completed: int, stage: str | None = None) -> None:
                    nonlocal current_batch
                    
                    # Calculate batch number from completed items
                    if completed > 0 and completed % batch_size == 0:
                        current_batch = min(completed // batch_size + 1, total_batches)
                    
                    # Calculate percentage based on completed items
                    percent = min(100, int(completed * 100 / _qty))
                    
                    # Calculate batch percentage
                    batch_start = (current_batch - 1) * batch_size
                    batch_items_done = completed - batch_start if completed > batch_start else 0
                    batch_items_total = min(batch_size, _qty - batch_start)
                    batch_percent = min(100, int(batch_items_done * 100 / batch_items_total if batch_items_total > 0 else 100))
                    
                    # Update main task with Brazilian colors - simple like the example
                    progress.update(
                        search_task,
                        description=f"[bright_green]Gerando {_qty} amostras... [bright_yellow]{percent}%[/]"
                    )
                    
                    # Update batch task with Brazilian colors
                    progress.update(
                        batch_task,
                        visible=True,
                        description=f"[bright_green]Lote [bright_yellow]{current_batch}[/bright_yellow]/[bright_yellow]{total_batches}[/bright_yellow]: [bright_yellow]{batch_percent}%[/]"
                    )
                    
                    # Update API task with Brazilian colors if relevant
                    if api_task and stage and 'API' in stage:
                        progress.update(api_task, visible=True)
                        if 'starting' in stage.lower() or 'connecting' in stage.lower():
                            progress.update(
                                api_task, 
                                completed=0.2, 
                                description=f'[bright_yellow]API: Conectando... (Lote {current_batch})'
                            )
                        elif 'processing' in stage.lower():
                            progress.update(
                                api_task, 
                                completed=0.6, 
                                description=f'[bright_yellow]API: Processando... (Lote {current_batch})'
                            )
                        elif 'completed' in stage.lower():
                            progress.update(
                                api_task, 
                                completed=1.0, 
                                description=f'[bright_yellow]API: Concluído (Lote {current_batch})'
                            )
                
                # Run the actual sampler function with our async progress callback
                results = await sampler_sample(
                    qty=_qty,
                    q=None,
                    city_only=city_only,
                    state_abbr_only=state_abbr_only,
                    state_full_only=state_full_only,
                    only_cep=only_cep,
                    cep_without_dash=cep_without_dash,
                    make_api_call=_make_api_call,
                    time_period=time_period,
                    return_only_name=return_only_name,
                    name_raw=name_raw,
                    json_path=json_path,
                    names_path=names_path,
                    middle_names_path=middle_names_path,
                    only_surname=only_surname,
                    top_40=top_40,
                    with_only_one_surname=with_only_one_surname,
                    always_middle=always_middle,
                    only_middle=only_middle,
                    always_cpf=always_cpf,
                    always_pis=always_pis,
                    always_cnpj=always_cnpj,
                    always_cei=always_cei,
                    always_rg=always_rg,
                    always_phone=_always_phone,
                    only_cpf=only_cpf,
                    only_pis=only_pis,
                    only_cnpj=only_cnpj,
                    only_cei=only_cei,
                    only_rg=only_rg,
                    only_fone=only_fone,
                    include_issuer=include_issuer,
                    only_document=only_document,
                    surnames_path=surnames_path,
                    locations_path=locations_path,
                    save_to_jsonl=_save_to_jsonl,
                    all_data=_all_data,
                    append_to_jsonl=append_to_jsonl,
                    batch_size=batch_size,
                    num_workers=num_workers,
                    progress_callback=progress_callback,
                )
            
            # Show completion message with Brazilian colors
            console.print(Panel(
                "\n".join([
                    f"[bright_green]✓[/] [bright_yellow]{_qty}[/] amostras geradas com sucesso!",
                    f"[bright_green]⏱️[/] Processamento concluído com sucesso!",
                    f"[bright_green]💾[/] {f'Resultados salvos em [bright_yellow]{save_to_jsonl}[/]' if save_to_jsonl else 'Resultados exibidos no console'}"
                ]),
                title="[bright_green]🇧🇷 Processamento Concluído[/bright_green]",
                border_style="bright_yellow",
                expand=False,
                padding=(1, 2)
            ))
            
            return results
            
        except Exception as e:
            logger.error(f"Error: {e}")
            console.print(Panel(
                f"[red]Erro: {e}[/red]",
                title="[red]Falha no Processamento[/red]",
                border_style="red"
            ))
            raise typer.Exit(code=1) from e

    # Run the coroutine with asyncio
    return asyncio.run(run_sample())

if __name__ == "__main__":
    app() 