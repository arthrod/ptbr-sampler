import os
import sys
import asyncio
from datetime import timedelta, timezone
from pathlib import Path
from typing import Any, Optional

# Import uvloop for faster asyncio performance
import uvloop

# Shut down standard logging to prevent INFO logs from libraries
import logging
logging.getLogger().setLevel(logging.WARNING)
for handler in logging.getLogger().handlers:
    handler.setLevel(logging.WARNING)

from async_typer import AsyncTyper
from typer import Option, Exit
from loguru import logger
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

# Handle imports for both direct script execution and module import
try:
    # Try relative imports first (when imported as a module)
    from .br_name_class import NameComponents, TimePeriod
    from .sampler import sample as sampler_sample
except ImportError:
    # Fall back to absolute imports if relative imports fail (when run as script)
    from ptbr_sampler.br_name_class import NameComponents, TimePeriod
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

console = Console()
app = AsyncTyper(help='BR data sampler CLI', add_completion=False)

# Define options at module level organized by panels
# Basic options
DEFAULT_QTY = Option(1, '--qty', '-q', help='Number of samples to generate', rich_help_panel='Basic Options')
ALL_DATA = Option(False, '--all', '-a', help='Include all possible data in the generated samples', rich_help_panel='Basic Options')
SAVE_TO_JSONL = Option(None, '--save-to-jsonl', '-sj', help='Save generated samples to a JSONL file', rich_help_panel='Basic Options')
APPEND_TO_JSONL = Option(True, '--append', '-ap', help='Append to JSONL file instead of overwriting', rich_help_panel='Basic Options')
# New convenience options
BATCH = Option(
    50,
    '--batch',
    '-b',
    help='Maximum samples per batch before saving (processes large requests in smaller chunks)',
    rich_help_panel='Basic Options',
)
EASY = Option(
    None, '--easy', '-e', help='Easy mode with integer qty (enables API calls, all data, and auto-saves)', rich_help_panel='Basic Options'
)

# Location options
CITY_ONLY = Option(False, '--city-only', '-c', help='Return only city names', rich_help_panel='Location Options')
STATE_ABBR_ONLY = Option(
    False, '--state-abbr-only', '-sa', help='Return only state abbreviations', rich_help_panel='Location Options'
)
STATE_FULL_ONLY = Option(False, '--state-full-only', '-sf', help='Return only full state names', rich_help_panel='Location Options')
ONLY_CEP = Option(False, '--only-cep', '-oc', help='Return only CEP', rich_help_panel='Location Options')
CEP_WITHOUT_DASH = Option(False, '--cep-without-dash', '-nd', help='Return CEP without dash', rich_help_panel='Location Options')
MAKE_API_CALL = Option(
    False,
    '--make-api-call',
    '-mac',
    help='Make API calls to retrieve real CEP data instead of generating synthetic address data',
    rich_help_panel='Location Options',
)

# Name options
TIME_PERIOD = Option(
    TimePeriod.UNTIL_2010, '--time-period', '-t', help='Time period for name sampling', rich_help_panel='Name Options'
)
RETURN_ONLY_NAME = Option(
    False, '--return-only-name', '-rn', help='Return only the name without location', rich_help_panel='Name Options'
)
NAME_RAW = Option(False, '--name-raw', '-r', help='Return names in raw format (all caps)', rich_help_panel='Name Options')
ONLY_SURNAME = Option(False, '--only-surname', '-s', help='Return only surname', rich_help_panel='Name Options')
TOP_40 = Option(False, '--top-40', '-t40', help='Use only top 40 surnames', rich_help_panel='Name Options')
WITH_ONLY_ONE_SURNAME = Option(
    False, '--one-surname', '-os', help='Return only one surname instead of two', rich_help_panel='Name Options'
)
ALWAYS_MIDDLE = Option(False, '--always-middle', '-am', help='Always include a middle name', rich_help_panel='Name Options')
ONLY_MIDDLE = Option(False, '--only-middle', '-om', help='Return only middle name', rich_help_panel='Name Options')

# Document options
ONLY_DOCUMENT = Option(False, '--only-document', '-od', help='Return only documents', rich_help_panel='Document Options')
ALWAYS_CPF = Option(True, '--always-cpf', '-ac', help='Always include CPF', rich_help_panel='Document Options')
ALWAYS_PIS = Option(False, '--always-pis', '-ap', help='Always include PIS', rich_help_panel='Document Options')
ALWAYS_CNPJ = Option(False, '--always-cnpj', '-acn', help='Always include CNPJ', rich_help_panel='Document Options')
ALWAYS_CEI = Option(False, '--always-cei', '-ace', help='Always include CEI', rich_help_panel='Document Options')
ALWAYS_RG = Option(True, '--always-rg', '-ar', help='Always include RG', rich_help_panel='Document Options')
ALWAYS_PHONE = Option(True, '--always-phone', '-aph', help='Always include phone number', rich_help_panel='Local e Fone')
ONLY_CPF = Option(False, '--only-cpf', '-ocpf', help='Return only CPF', rich_help_panel='Document Options')
ONLY_PIS = Option(False, '--only-pis', '-op', help='Return only PIS', rich_help_panel='Document Options')
ONLY_CNPJ = Option(False, '--only-cnpj', '-ocn', help='Return only CNPJ', rich_help_panel='Document Options')
ONLY_CEI = Option(False, '--only-cei', '-oce', help='Return only CEI', rich_help_panel='Document Options')
ONLY_RG = Option(False, '--only-rg', '-or', help='Return only RG', rich_help_panel='Document Options')
ONLY_FONE = Option(False, '--only-fone', '-of', help='Return only phone number', rich_help_panel='Local e Fone')
INCLUDE_ISSUER = Option(
    True, '--include-issuer', '-ii', help='Include issuer in RG (default: True)', rich_help_panel='Document Options'
)

# Data source options
JSON_PATH = Option(
    'ptbr_sampler/data/cities_with_ceps.json',
    '--json-path',
    '-j',
    help='Path to the cities and CEPs data JSON file',
    rich_help_panel='Data Source Options',
)
NAMES_PATH = Option(
    'ptbr_sampler/data/names_data.json', '--names-path', '-np', help='Path to the first names data JSON file', rich_help_panel='Data Source Options'
)
MIDDLE_NAMES_PATH = Option(
    'ptbr_sampler/data/middle_names.json',
    '--middle-names-path',
    '-mnp',
    help='Path to the middle names JSON file',
    rich_help_panel='Data Source Options',
)
SURNAMES_PATH = Option(
    'ptbr_sampler/data/surnames_data.json', '--surnames-path', '-sp', help='Path to the surnames JSON file', rich_help_panel='Data Source Options'
)
LOCATIONS_PATH = Option(
    'ptbr_sampler/data/locations_data.json',
    '--locations-path',
    '-lp',
    help='Path to the locations data JSON file',
    rich_help_panel='Data Source Options',
)


def _format_document_lines(doc: dict[str, str]) -> list[str]:
    """Format document information into display lines.

    This function processes document information and formats it into
    a list of strings suitable for display. It handles special
    formatting for RG numbers which include state information.

    Args:
        doc: Dictionary containing document information
             Keys can be: 'cpf', 'pis', 'cnpj', 'cei', 'rg', 'phone'

    Returns:
        List of formatted document strings
    """
    doc_lines = []

    # Handle documents in a specific order
    if 'cpf' in doc:
        doc_lines.append(f'CPF: {doc["cpf"]}')
    if 'rg' in doc:
        if '/' in doc['rg']:  # RG with state information
            rg_num, state = doc['rg'].split('/')
            doc_lines.append(f'RG: {rg_num} ({state})')
        else:
            doc_lines.append(f'RG: {doc["rg"]}')
    if 'pis' in doc:
        doc_lines.append(f'PIS: {doc["pis"]}')
    if 'cnpj' in doc:
        doc_lines.append(f'CNPJ: {doc["cnpj"]}')
    if 'cei' in doc:
        doc_lines.append(f'CEI: {doc["cei"]}')
    if 'phone' in doc:
        doc_lines.append(f'Telefone: {doc["phone"]}')

    return doc_lines


def create_results_table(
    results: list[tuple[str | None, NameComponents, dict[str, Any], dict[str, Any]]],
    title: str,
    return_only_name: bool = False,
    only_location: bool = False,
    only_document: bool = False,
) -> Table:
    """Create a formatted table for displaying Brazilian sample data results.

    This function creates a rich, formatted table that handles complex Brazilian name patterns,
    including compound names, surnames with prefixes, and various document types.

    Args:
        results: List of tuples containing:
                - location string
                - NameComponents object (first_name, middle_name, surname)
                - Dictionary of documents
                - Dictionary of address data (street, neighborhood, building_number)
        title: The title to display at the top of the table
        return_only_name: If True, displays only name information
        only_location: If True, displays only location information
        only_document: If True, displays only document information

    Returns:
        Rich Table object formatted according to specifications

    The table structure adapts based on the content type:
    - Full display: ID, Name, Middle Name, Surname, Location, Documents
    - Name only: ID, Name, Middle Name, Surname
    - Location only: ID, Location
    - Document only: ID, Documents
    """
    table = Table(
        title=title,
        show_lines=True,  # Add horizontal lines between rows
        show_edge=True,  # Show table edges
        padding=(0, 1),  # Add minimal padding for readability
        title_style='bright_yellow',
        border_style='blue',
        header_style='bright_green',
        expand=True,
        collapse_padding=True,
    )

    # Add columns based on display mode
    table.add_column('Id', justify='right', style='bright_yellow', no_wrap=True, width=5)

    if only_document:
        table.add_column('Documentos', style='green', overflow='fold', max_width=50)
    else:
        if not only_location:
            # Name columns
            table.add_column('Nome', style='bright_green', width=21)
            table.add_column('Nome do Meio', style='green', width=22)
            table.add_column('Sobrenome', style='green', width=23)

        if not return_only_name:
            # Location and documents columns
            table.add_column('Local', style='bright_yellow', width=30)
            table.add_column('Logradouro', style='yellow', width=50)
            table.add_column('Documentos', style='green', overflow='fold', width=28)

    # Process and add rows
    for idx, result in enumerate(results, 1):
        if isinstance(result, tuple):
            if len(result) == 4:  # New format with address data
                location, name_components, documents, address_data = result
            else:  # Old format without address data
                location, name_components, documents = result
                address_data = {}

            # Format documents string
            doc_lines = _format_document_lines(documents)
            doc_str = '\n'.join(doc_lines)

            if only_document:
                table.add_row(str(idx), doc_str)
            else:
                row = [str(idx)]

                # Add name components if not location-only
                if not only_location and name_components:
                    row.extend([name_components.first_name, name_components.middle_name or '', name_components.surname])

                # Add location and documents if not name-only
                if not return_only_name:
                    # Combine address data into a single logradouro field
                    street = address_data.get('street', '')
                    neighborhood = address_data.get('neighborhood', '')
                    building_number = address_data.get('building_number', '')

                    # Format the logradouro: street, building_number - neighborhood
                    logradouro = ''
                    if street:
                        logradouro = street
                        if building_number:
                            logradouro += f', {building_number}'
                        if neighborhood:
                            logradouro += f' - {neighborhood}'
                    elif neighborhood:
                        logradouro = neighborhood
                        if building_number:
                            logradouro += f', {building_number}'

                    # Add phone number to logradouro if available
                    phone = address_data.get('phone', '')
                    if phone:
                        if logradouro:
                            logradouro += f'\nTelefone: {phone}'
                        else:
                            logradouro = f'Telefone: {phone}'

                    row.extend([location or '', logradouro, doc_str])

                table.add_row(*row)
        else:
            # Handle plain string results
            table.add_row(str(idx), result)

    return table


@app.async_command()
async def sample(
    qty: int = DEFAULT_QTY,
    city_only: bool = CITY_ONLY,
    state_abbr_only: bool = STATE_ABBR_ONLY,
    state_full_only: bool = STATE_FULL_ONLY,
    only_cep: bool = ONLY_CEP,
    cep_without_dash: bool = CEP_WITHOUT_DASH,
    make_api_call: bool = MAKE_API_CALL,
    time_period: TimePeriod = TIME_PERIOD,
    return_only_name: bool = RETURN_ONLY_NAME,
    name_raw: bool = NAME_RAW,
    json_path: Path = JSON_PATH,
    names_path: Path = NAMES_PATH,
    middle_names_path: Path = MIDDLE_NAMES_PATH,
    only_surname: bool = ONLY_SURNAME,
    top_40: bool = TOP_40,
    with_only_one_surname: bool = WITH_ONLY_ONE_SURNAME,
    always_middle: bool = ALWAYS_MIDDLE,
    only_middle: bool = ONLY_MIDDLE,
    always_cpf: bool = ALWAYS_CPF,
    always_pis: bool = ALWAYS_PIS,
    always_cnpj: bool = ALWAYS_CNPJ,
    always_cei: bool = ALWAYS_CEI,
    always_rg: bool = ALWAYS_RG,
    always_phone: bool = ALWAYS_PHONE,
    only_cpf: bool = ONLY_CPF,
    only_pis: bool = ONLY_PIS,
    only_cnpj: bool = ONLY_CNPJ,
    only_cei: bool = ONLY_CEI,
    only_rg: bool = ONLY_RG,
    only_fone: bool = ONLY_FONE,
    include_issuer: bool = INCLUDE_ISSUER,
    only_document: bool = ONLY_DOCUMENT,
    surnames_path: Path = SURNAMES_PATH,
    locations_path: Path = LOCATIONS_PATH,
    save_to_jsonl: str = SAVE_TO_JSONL,
    all_data: bool = ALL_DATA,
    batch: int = BATCH,
    easy: int = EASY,
    append_to_jsonl: bool = APPEND_TO_JSONL,
) -> None:
    """Generate random Brazilian samples with comprehensive information.

    This function generates random Brazilian location, name, and document samples
    based on the provided parameters. It handles various combinations of output
    formats and ensures proper state handling for document generation.

    Args:
        qty: Number of samples to generate
        city_only: Return only city names
        state_abbr_only: Return only state abbreviations
        state_full_only: Return only full state names
        only_cep: Return only CEP
        cep_without_dash: Format CEP without dash
        time_period: Time period for name sampling
        return_only_name: Return only names without location
        name_raw: Return names in raw format (all caps)
        json_path: Path to city/state data JSON file
        names_path: Path to first names data file
        middle_names_path: Path to middle names data file
        only_surname: Return only surnames
        top_40: Use only top 40 surnames
        with_only_one_surname: Use single surname
        always_middle: Always include middle name
        only_middle: Return only middle names
        always_cpf: Include CPF in documents
        always_pis: Include PIS in documents
        always_cnpj: Include CNPJ in documents
        always_cei: Include CEI in documents
        always_rg: Include RG in documents
        only_cpf: Generate only CPF
        only_pis: Generate only PIS
        only_cnpj: Generate only CNPJ
        only_cei: Generate only CEI
        only_rg: Generate only RG
        include_issuer: Include issuing state in RG
        only_document: Return only documents
        surnames_path: Path to surnames data file
        locations_path: Path to locations data JSON file
        save_to_jsonl: Path to save generated samples as JSONL
        all_data: Include all possible data in the generated samples
        batch: Maximum number of samples per batch before saving to file
        easy: Easy mode with integer qty (enables API calls, all data, and auto-saves)
        append_to_jsonl: Append to JSONL file instead of overwriting

    Raises:
        typer.Exit: If an error occurs during execution
    """

    try:
        # Process easy mode if specified
        if easy is not None:
            console.print(Panel('[bright_yellow]Modo Fácil Ativado[/bright_yellow]', 
                               title="[bright_green]PTBR Sampler[/bright_green]", 
                               border_style="green"))
            logger.info(f'Easy mode enabled with quantity: {easy}')
            qty = easy
            make_api_call = True
            all_data = True
            always_phone = True
            # Only set default path if user hasn't specified one
            if save_to_jsonl is None:
                save_to_jsonl = 'output/output.jsonl'

            # Ensure output directory exists
            output_path = Path(save_to_jsonl)
            if output_path.parent != Path() and not output_path.parent.exists():
                console.print(f'[yellow]Creating output directory: {output_path.parent}[/yellow]')
                logger.info(f'Creating output directory: {output_path.parent}')
                output_path.parent.mkdir(parents=True, exist_ok=True)

        # Set up batch processing if enabled
        use_batches = True
        batch_size = BATCH

        if batch is not None and batch > 0 and save_to_jsonl:
            batch_size = min(batch, qty)  # Ensure batch size doesn't exceed total quantity
            use_batches = batch_size < qty  # Only use batches if we have multiple batches

            if use_batches:
                total_batches = (qty + batch_size - 1) // batch_size
                console.print(Panel(
                    f"[bright_green]Processando[/bright_green] [bright_yellow]{qty}[/bright_yellow] [bright_green]amostras em[/bright_green] [bright_yellow]{total_batches}[/bright_yellow] [bright_green]lotes de[/bright_green] [bright_yellow]{batch_size}[/bright_yellow] [bright_green]cada[/bright_green]",
                    title="[bright_green]Configuração de Lotes[/bright_green]",
                    border_style="bright_yellow"
                ))
                logger.info(f'Batch mode enabled: {qty} samples in batches of {batch_size}')
            else:
                console.print(f'[bright_green]Lote único:[/bright_green] [yellow]tamanho do lote ({batch_size}) é maior ou igual à quantidade total ({qty})[/yellow]')
                logger.info(f'Single batch mode: batch size {batch_size} >= quantity {qty}')

        # Show configuration summary for batch or easy modes
        if batch is not None or easy is not None:
            config_items = []
            
            config_items.append(f"[bright_green]Quantidade:[/bright_green] [bright_yellow]{qty}[/bright_yellow]")
            config_items.append(f"[bright_green]Chamada de API:[/bright_green] [{'bright_yellow' if make_api_call else 'dim yellow'}]{make_api_call}[/]")
            config_items.append(f"[bright_green]Todos os dados:[/bright_green] [{'bright_yellow' if all_data else 'dim yellow'}]{all_data}[/]")
            config_items.append(f"[bright_green]Incluir telefone:[/bright_green] [{'bright_yellow' if always_phone else 'dim yellow'}]{always_phone}[/]")
            
            if save_to_jsonl:
                save_mode = '[bright_yellow]append[/]' if append_to_jsonl else '[yellow]overwrite[/]'
                config_items.append(f"[bright_green]Salvar em:[/bright_green] [bright_yellow]{save_to_jsonl}[/] ({save_mode})")
                if use_batches:
                    config_items.append(f"[bright_green]Tamanho do lote:[/bright_green] [bright_yellow]{batch_size}[/] amostras")

            config_text = "\n".join(config_items)
            console.print(Panel(config_text, 
                             title="[bright_green]Configuração do Gerador[/bright_green]",
                             border_style="bright_yellow", 
                             expand=False))

            logger.info(f'Configuration: qty={qty}, api={make_api_call}, all_data={all_data}, file={save_to_jsonl}, append={append_to_jsonl}')

        # Process in batches or as a single run
        all_results = []

        if use_batches:
            # Use batched processing with progress display
            logger.info(f'Starting batch processing of {qty} samples')
            
            # Calculate total batches for display
            total_batches = (qty + batch_size - 1) // batch_size
            samples_completed = 0

            # Use a simplified progress display with Brazilian colors
            with Progress() as progress:
                # Main task - similar to the example
                main_task = progress.add_task(f'[bright_green]Gerando {qty} amostras...', total=None)
                
                # API task if needed
                api_task = None
                if make_api_call:
                    api_task = progress.add_task('[bright_yellow]Chamadas de API:', visible=False, total=None)
                
                # Batch task
                batch_task = progress.add_task(f'[bright_green]Lote atual:', visible=False, total=None)
                
                # Process each batch
                first_batch = True
                while samples_completed < qty:
                    # Calculate batch size for this iteration
                    current_batch_size = min(batch_size, qty - samples_completed)
                    batch_num = samples_completed // batch_size + 1
                    
                    # Update batch task
                    progress.update(
                        batch_task, 
                        visible=True, 
                        description=f'[bright_green]Lote [bright_yellow]{batch_num}[/bright_yellow]/[bright_yellow]{total_batches}[/bright_yellow]: Preparando...'
                    )
                    
                    # Create progress callback
                    def create_progress_callback(samples_completed_val: int, batch_num_val: int, current_batch_size_val: int) -> callable:
                        async def progress_callback(completed: int, stage: str | None = None) -> None:
                            # Use explicit parameter binding to avoid closure issues
                            nonlocal samples_completed_val, batch_num_val, current_batch_size_val
                            
                            # Calculate total progress
                            total_completed = min(samples_completed_val + completed, qty)
                            total_percent = min(100, int(total_completed * 100 / qty))
                            
                            # Calculate batch progress
                            batch_percent = min(100, int(completed * 100 / current_batch_size_val))
                            
                            # Update main task - simple like example
                            progress.update(
                                main_task, 
                                description=f'[bright_green]Gerando {qty} amostras... [bright_yellow]{total_percent}%[/]'
                            )
                            
                            # Update batch task
                            progress.update(
                                batch_task,
                                description=f'[bright_green]Lote [bright_yellow]{batch_num_val}[/bright_yellow]/[bright_yellow]{total_batches}[/bright_yellow]: [bright_yellow]{batch_percent}%[/]'
                            )
                            
                            # Update API task if needed
                            if api_task and stage and 'API' in stage:
                                progress.update(api_task, visible=True)
                                if 'starting' in stage.lower() or 'connecting' in stage.lower():
                                    progress.update(
                                        api_task,
                                        description=f'[bright_yellow]API: Conectando... (Lote {batch_num_val})'
                                    )
                                elif 'processing' in stage.lower():
                                    progress.update(
                                        api_task,
                                        description=f'[bright_yellow]API: Processando... (Lote {batch_num_val})'
                                    )
                                elif 'completed' in stage.lower():
                                    progress.update(
                                        api_task,
                                        description=f'[bright_yellow]API: Concluído (Lote {batch_num_val})'
                                    )
                        return progress_callback

                    # Create the callback with current values
                    progress_callback = create_progress_callback(samples_completed, batch_num, current_batch_size)

                    # Process the current batch
                    try:
                        batch_results = await sampler_sample(
                            qty=current_batch_size,
                            q=None,
                            city_only=city_only,
                            state_abbr_only=state_abbr_only,
                            state_full_only=state_full_only,
                            only_cep=only_cep,
                            cep_without_dash=cep_without_dash,
                            make_api_call=make_api_call,
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
                            always_phone=always_phone,
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
                            save_to_jsonl=save_to_jsonl,
                            all_data=all_data,
                            progress_callback=progress_callback,
                            append_to_jsonl=(append_to_jsonl or not first_batch),  # Force append for all batches after the first
                        )
                        logger.info(f'Batch {batch_num} processed successfully')
                    except Exception as e:
                        logger.error(f'Error processing batch {batch_num}: {e}')
                        raise

                    # Force append mode after the first batch
                    first_batch = False

                    # Save this batch's results
                    if isinstance(batch_results, list):
                        all_results.extend(batch_results)
                    else:
                        all_results.append(batch_results)

                    # Update completed count
                    samples_completed += current_batch_size

                    # Mark the batch as completed
                    progress.update(batch_task, completed=current_batch_size, status=f'[bright_yellow]Concluído - Salvo em {save_to_jsonl}[/]')

                    logger.info(f'Batch {batch_num} saved to {save_to_jsonl}')

                # All batches are complete
                progress.update(main_task, completed=qty, status='[bright_green]Todos os lotes concluídos![/]')
                progress.update(batch_task, visible=False)
                if api_task:
                    progress.update(api_task, visible=False)

                # Show completion message
                total_batches = (qty + batch_size - 1) // batch_size
                logger.info(f'All {total_batches} batches completed successfully. Total samples: {qty}')
                
                # Create a beautiful completion panel with Brazilian colors
                completion_text = [
                    f"[bright_green]✓[/] [bright_yellow]{qty}[/] amostras geradas com sucesso em [bright_yellow]{total_batches}[/] lotes!",
                    f"[bright_green]⏱️[/] Processamento concluído com sucesso!",
                ]
                if save_to_jsonl:
                    completion_text.append(f"[bright_green]💾[/] Todos os resultados salvos em [bright_yellow]{save_to_jsonl}[/]")
                
                console.print(Panel(
                    "\n".join(completion_text),
                    title="[bright_green]🇧🇷 Processamento Concluído[/bright_green]",
                    border_style="bright_yellow",
                    expand=False,
                    padding=(1, 2)
                ))

        else:
            # Standard processing (non-batched) with enhanced progress display
            logger.info(f'Starting standard (non-batched) processing of {qty} samples')
            # Brazilian flag colors theme: green and yellow with blue details
            with Progress(
                SpinnerColumn(spinner_name="dots", style="bright_yellow"),
                TextColumn("[bright_green]{task.description}"),
                BarColumn(complete_style='bright_green', finished_style='green', pulse_style='bright_yellow'),
                TaskProgressColumn(style="bright_yellow"),
                TextColumn("[blue]{task.fields[status]}[/]"),
                console=console,
                expand=True,
                refresh_per_second=15  # Increase refresh rate for smoother animation
            ) as progress:
                main_task = progress.add_task(
                    f"[bright_green]Gerando {qty} amostras...", 
                    total=qty, 
                    status="Iniciando"
                )

                # Create a task for API calls if make_api_call is true
                api_task = None
                if make_api_call:
                    api_task = progress.add_task(
                        "[bright_yellow]🌐 Chamadas de API...", 
                        visible=False, 
                        total=1.0, 
                        status=""
                    )
                
                # Create stats task with emojis and bright colors
                stats_task = progress.add_task(
                    "[bright_green]📊 Estatísticas...",
                    total=1.0,
                    completed=1.0,
                    visible=True,
                    status=f"[bright_green]🌐 Modo API:[/] [{'bright_yellow' if make_api_call else 'dim blue'}]{make_api_call}[/]"
                )

                # Call the sample function with progress updates
                async def progress_callback(completed: int, stage: str | None = None) -> None:
                    # Log significant progress stages
                    if stage and completed % max(1, qty // 10) == 0:
                        logger.debug(f'Progress: {completed}/{qty} samples - {stage}')

                    # Calculate percentage
                    percent = min(100, int(completed * 100 / qty))
                    
                    # Update the main task with percentage
                    progress.update(
                        main_task, 
                        completed=completed, 
                        status=f"[blue]{stage or ''}[/] [bright_yellow]{percent}%[/]"
                    )

                    # Update stats with current progress and emojis
                    stats_text = [
                        f"[bright_green]📈 Progresso:[/] [bright_yellow]{completed}[/] de [bright_yellow]{qty}[/]",
                        f"[bright_green]🔢 Porcentagem:[/] [bright_yellow]{percent}%[/]",
                        f"[bright_green]🌐 Modo API:[/] [{'bright_yellow' if make_api_call else 'dim blue'}]{make_api_call}[/]"
                    ]
                    
                    if stage:
                        stats_text.append(f"[bright_green]📝 Status:[/] [blue]{stage}[/]")
                        
                    progress.update(
                        stats_task,
                        visible=True,
                        status="\n".join(stats_text)
                    )

                    # Update API task if relevant
                    if api_task and stage:
                        if 'API' in stage:
                            progress.update(api_task, visible=True)
                            if 'starting' in stage.lower() or 'connecting' in stage.lower():
                                logger.info('API calls starting')
                                progress.update(
                                    api_task, 
                                    completed=0.2, 
                                    status='[bright_yellow]Conectando...[/]'
                                )
                            elif 'processing' in stage.lower():
                                logger.info('Processing API responses')
                                progress.update(
                                    api_task, 
                                    completed=0.6, 
                                    status='[bright_yellow]Processando respostas...[/]'
                                )
                            elif 'completed' in stage.lower():
                                logger.info('API calls completed')
                                progress.update(
                                    api_task, 
                                    completed=1.0, 
                                    status='[bright_green]Concluído![/]'
                                )

                # Call the sample function from the sampler module with all parameters
                try:
                    all_results = await sampler_sample(
                        qty=qty,
                        q=None,  # We don't use this alias in the CLI
                        city_only=city_only,
                        state_abbr_only=state_abbr_only,
                        state_full_only=state_full_only,
                        only_cep=only_cep,
                        cep_without_dash=cep_without_dash,
                        make_api_call=make_api_call,
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
                        always_phone=always_phone,
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
                        save_to_jsonl=save_to_jsonl,
                        all_data=all_data,
                        progress_callback=progress_callback,
                        append_to_jsonl=append_to_jsonl,
                    )
                    logger.info(f'All {qty} samples processed successfully')
                except Exception as e:
                    logger.error(f'Error processing samples: {e}')
                    raise

                # Ensure progress is complete
                progress.update(main_task, completed=qty, status='[bright_green]Concluído![/]')
                if api_task:
                    progress.update(api_task, visible=False)

                # Show completion message
                logger.info(f'Sample generation completed. Total samples: {qty}')
                
                # Create a beautiful completion panel with Brazilian colors
                completion_text = [
                    f"[bright_green]✓[/] [bright_yellow]{qty}[/] amostras geradas com sucesso!",
                    f"[bright_green]⏱️[/] Processamento concluído com sucesso!",
                ]
                if save_to_jsonl:
                    completion_text.append(f"[bright_green]💾[/] Resultados salvos em [bright_yellow]{save_to_jsonl}[/]")
                
                console.print(Panel(
                    "\n".join(completion_text),
                    title="[bright_green]🇧🇷 Processamento Concluído[/bright_green]",
                    border_style="bright_yellow",
                    expand=False,
                    padding=(1, 2)
                ))
    except Exception as e:
        logger.error(f'Error in sample generation: {e}')
        console.print(f'[red]Error: {e!s}[/red]')
        raise Exit(code=1) from e

async def main() -> None:
    """Entry point for the CLI application.

    This function serves as the main entry point for the command-line interface.
    It initializes and runs the AsyncTyper application with all configured commands
    and options.
    """
    await app()


if __name__ == '__main__':
    # Add parent directory to path for direct script execution
    import sys
    from pathlib import Path

    # Get the project root directory (parent of the ptbr_sampler package)
    project_root = Path(__file__).parent.parent.absolute()

    # Add the project root to the Python path if it's not already there
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Install uvloop as the default event loop policy
    uvloop.install()
    
    # Run the main function with the uvloop event loop
    asyncio.run(main())
