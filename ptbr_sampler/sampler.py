"""
Brazilian Sample Generator

Core functionality for generating Brazilian name, location, and document samples.
"""

import asyncio
import json
from pathlib import Path
import random
from typing import List, Optional

import aiofiles
from loguru import logger
from pydantic import BaseModel, Field

from ptbr_sampler.utils.phone import generate_phone_number

from .br_location_class import BrazilianLocationSampler
from .br_name_class import BrazilianNameSampler, NameComponents, TimePeriod
from .document_sampler import DocumentSampler


# Define Pydantic models for streamlined processing
class LocationItem(BaseModel):
    """Model representing location data for a single person"""
    cep: str = ""
    city_name: str = ""
    city_uf: str = ""  # State abbreviation (UF)
    state: str = ""    # Full state name
    phone: str = ""
    street: str = ""
    building_number: str = ""
    neighborhood: str = ""
    
    # Person data
    name: str = ""
    middle_name: Optional[str] = None
    surnames: str = ""
    
    # Documents
    cpf: str = ""
    rg: str = ""
    pis: str = ""
    cnpj: str = ""
    cei: str = ""


class LocationBatch(BaseModel):
    """Model representing a batch of location items"""
    items: List[LocationItem] = Field(default_factory=list)


async def save_to_jsonl_file(data: List[LocationItem], filename: str, append: bool = True) -> None:
    """Save generated samples to a JSONL file asynchronously.

    Args:
        data: List of LocationItem objects containing sample data
        filename: Path to the output JSONL file
        append: If True, append to existing file instead of overwriting
    """
    mode = 'a' if append else 'w'

    # Create a directory for the file if it doesn't exist
    file_path = Path(filename)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    async with aiofiles.open(file_path, mode, encoding='utf-8') as f:
        for item in data:
            await f.write(json.dumps(item.dict(), ensure_ascii=False) + '\n')


async def get_address_data_batch(location_items: List[LocationItem], make_api_call: bool = False, progress_callback: callable = None, num_workers: int = 100) -> List[LocationItem]:
    """
    Get address data for multiple CEPs and update the LocationItems.

    Args:
        location_items: List of LocationItem objects to be updated
        make_api_call: Whether to make API calls or generate data
        progress_callback: Optional callback function to report progress
        num_workers: Number of workers to use for API calls (default: 100)

    Returns:
        Updated list of LocationItem objects with address data
    """
    if not location_items:
        return []
    
    # Extract CEPs from location items
    ceps = [item.cep for item in location_items]
    
    logger.debug(f'Getting address data for {len(ceps)} CEPs (API mode: {make_api_call})')
    
    # Create a copy of the location items to avoid modifying the original
    updated_items = [item.copy(deep=True) for item in location_items]

    if make_api_call:
        # Use cep_wrapper to get real data for multiple CEPs
        from .utils.cep_wrapper import workers_for_multiple_cep

        # Format CEPs to remove dashes before API call
        formatted_ceps = [cep.replace('-', '') for cep in ceps]
        logger.info(f'Making API calls for {len(formatted_ceps)} CEPs with {num_workers} workers')

        # Update progress if callback is provided
        if progress_callback:
            await progress_callback(0, 'API calls: Connecting to service')

        try:
            # Get data from API - explicitly set workers to 100
            cep_data_list = await workers_for_multiple_cep(formatted_ceps, max_workers=num_workers)
            logger.info(f'Received API responses for {len(cep_data_list)} CEPs')

            # Update progress if callback is provided
            if progress_callback:
                await progress_callback(0, 'API calls: Processing responses')

            # Process each CEP result
            for i, cep_data in enumerate(cep_data_list):
                if i >= len(updated_items):
                    break
                
                # Skip if we can't process this data properly
                if not cep_data or (isinstance(cep_data, dict) and 'error' in cep_data):
                    continue
                
                # Handle dictionary and list responses
                data_to_use = None
                if isinstance(cep_data, dict) and 'error' not in cep_data:
                    data_to_use = cep_data
                elif isinstance(cep_data, list) and cep_data and isinstance(cep_data[0], dict):
                    data_to_use = cep_data[0]
                
                # Update the location item with the API data if available
                if data_to_use:
                    # Only update fields that are empty or missing in the original item
                    if not updated_items[i].street:
                        updated_items[i].street = data_to_use.get('street', '')
                    if not updated_items[i].neighborhood:
                        updated_items[i].neighborhood = data_to_use.get('neighborhood', '')
                    if not updated_items[i].building_number:
                        updated_items[i].building_number = str(random.randint(1, 999))
                    
                    # Don't override existing state/city values with API data
                    # This preserves names like "São Paulo" instead of abbreviations
        except Exception as e:
            logger.error(f'Error during API calls: {e}')
            
    else:
        # Generate fake data for each CEP
        logger.info(f'Generating synthetic address data for {len(ceps)} CEPs (offline mode)')
        
        for i, item in enumerate(updated_items):
            # Generate random address data if needed
            if not item.street:
                street_names = ['Rua', 'Avenida', 'Alameda', 'Travessa', 'Rodovia']
                item.street = f"{random.choice(street_names)} {random.randint(1, 100)}"
            
            if not item.neighborhood:
                neighborhood_names = ['Centro', 'Jardim', 'Vila', 'Bairro', 'Parque']
                item.neighborhood = f"{random.choice(neighborhood_names)} {random.randint(1, 50)}"
            
            if not item.building_number:
                item.building_number = str(random.randint(1, 999))

            # Update progress occasionally if callback is provided
            if progress_callback and i % max(1, len(ceps) // 10) == 0:
                await progress_callback(0, f'Generating address data: {i + 1}/{len(ceps)}')

    # Ensure all items have a building number
    for item in updated_items:
        if not item.building_number:
            item.building_number = str(random.randint(1, 999))

    # Final update for API calls completion
    if progress_callback and make_api_call:
        await progress_callback(0, 'API calls processing completed')

    return updated_items


async def process_and_save_in_batches(
    location_items: List[LocationItem],
    make_api_call: bool,
    save_to_jsonl: str | None,
    append_to_jsonl: bool,
    progress_callback: callable = None,
    batch_size: int = 100,
    num_workers: int = 100
) -> List[LocationItem]:
    """Process location items in batches, make API calls for each batch, and save results incrementally.
    
    Args:
        location_items: List of LocationItem objects to process
        make_api_call: Whether to make API calls or generate data
        save_to_jsonl: Path to save results as JSONL (if None, no saving is done)
        append_to_jsonl: Whether to append to existing JSONL file
        progress_callback: Optional callback function for progress updates
        batch_size: Number of items to process in each batch (default: 100)
        num_workers: Number of workers to use for API calls (default: 100)
        
    Returns:
        List of processed LocationItem objects
    """
    total_items = len(location_items)
    all_processed_items = []
    
    # Calculate number of batches - always use batch_size=100
    batch_size = 100  # Ensure batch size is always 100
    num_batches = (total_items + batch_size - 1) // batch_size  # ceiling division
    
    logger.info(f"Processing {total_items} items in {num_batches} batches of {batch_size}")
    
    for batch_idx in range(num_batches):
        start_idx = batch_idx * batch_size
        end_idx = min(start_idx + batch_size, total_items)
        current_batch_size = end_idx - start_idx
        
        logger.info(f"Processing batch {batch_idx + 1}/{num_batches} with {current_batch_size} items")
        
        if progress_callback:
            await progress_callback(start_idx, f"Processing batch {batch_idx + 1}/{num_batches}")
        
        # Get the batch of location items
        batch_items = location_items[start_idx:end_idx]
        
        # Process address data for the batch - pass num_workers=100
        processed_items = await get_address_data_batch(
            batch_items, 
            make_api_call, 
            progress_callback,
            num_workers=num_workers
        )
        
        # Add to the full list of processed items
        all_processed_items.extend(processed_items)
        
        # Save this batch if requested
        if save_to_jsonl:
            try:
                # For the first batch, we may need to overwrite the file
                current_append = append_to_jsonl if batch_idx > 0 else False
                if batch_idx == 0 and append_to_jsonl:
                    # For the first batch when appending, check if file exists
                    # If not, we'll create it (so use append=False)
                    file_path = Path(save_to_jsonl)
                    current_append = file_path.exists()
                
                logger.info(f"Saving batch {batch_idx + 1} with {len(processed_items)} results to {save_to_jsonl} (append={current_append})")
                
                # Save just this batch
                await save_to_jsonl_file(processed_items, save_to_jsonl, append=current_append)
                
                if progress_callback:
                    await progress_callback(end_idx, f"Saved batch {batch_idx + 1}/{num_batches}")
            except Exception as e:
                logger.error(f"Error saving batch {batch_idx + 1} to JSONL: {e}")
                print(f"Error saving batch {batch_idx + 1} to JSONL: {e}")
    
    return all_processed_items


async def sample(
    qty: int = 1,
    q: int | None = None,
    city_only: bool = False,
    state_abbr_only: bool = False,
    state_full_only: bool = False,
    only_cep: bool = False,
    cep_without_dash: bool = False,
    make_api_call: bool = False,
    time_period: TimePeriod = TimePeriod.UNTIL_2010,
    return_only_name: bool = False,
    name_raw: bool = False,
    json_path: str | Path = Path(__file__).parent / 'data' / 'location_data.json',
    names_path: str | Path = Path(__file__).parent / 'data' / 'names_data.json',
    middle_names_path: str | Path = Path(__file__).parent / 'data' / 'middle_names.json',
    only_surname: bool = False,
    top_40: bool = False,
    with_only_one_surname: bool = False,
    always_middle: bool = False,
    only_middle: bool = False,
    always_cpf: bool = False,
    always_pis: bool = False,
    always_cnpj: bool = False,
    always_cei: bool = False,
    always_rg: bool = False,
    always_phone: bool = False,
    only_cpf: bool = False,
    only_pis: bool = False,
    only_cnpj: bool = False,
    only_cei: bool = False,
    only_rg: bool = False,
    only_fone: bool = False,
    include_issuer: bool = False,
    only_document: bool = False,
    surnames_path: str | Path = Path(__file__).parent / 'data' / 'surnames_data.json',
    locations_path: str | Path = '',
    save_to_jsonl: str | None = None,
    all_data: bool = False,
    progress_callback: callable = None,
    append_to_jsonl: bool = True,
    batch_size: int = 100,
    num_workers: int = 100,
) -> List[LocationItem] | LocationItem:
    """Generate random Brazilian samples with comprehensive information.

    Args:
        qty: Number of samples to generate
        q: Alias for qty parameter (takes precedence if provided)
        city_only: Only include city information
        state_abbr_only: Only include state abbreviation
        state_full_only: Only include full state name
        only_cep: Only include CEP (postal code)
        cep_without_dash: Format CEP without dash
        make_api_call: Make API calls to get real address data
        time_period: Time period for name generation
        return_only_name: Only return name information (no location or documents)
        name_raw: Return name in raw format
        json_path: Path to JSON data file
        names_path: Path to names data file
        middle_names_path: Path to middle names data file
        only_surname: Only generate surnames
        top_40: Use only top 40 names
        with_only_one_surname: Generate only one surname
        always_middle: Always include middle name
        only_middle: Only generate middle names
        always_cpf: Always include CPF
        always_pis: Always include PIS
        always_cnpj: Always include CNPJ
        always_cei: Always include CEI
        always_rg: Always include RG
        always_phone: Always include phone number
        only_cpf: Only include CPF
        only_pis: Only include PIS
        only_cnpj: Only include CNPJ
        only_cei: Only include CEI
        only_rg: Only include RG
        only_fone: Only include phone
        include_issuer: Include issuer information for RG
        only_document: Only generate document information
        surnames_path: Path to surnames data file
        locations_path: Path to locations data file
        save_to_jsonl: Path to save results as JSONL
        all_data: Include all available data
        progress_callback: Callback function for progress updates
        append_to_jsonl: Append to existing JSONL file instead of overwriting
        batch_size: Number of items to process in each batch (default: 100)
        num_workers: Number of workers to use for API calls (default: 100)

    Returns:
        List of LocationItem objects or single LocationItem if qty=1
    """
    logger.info(f'Starting sample generation. qty={qty}, api={make_api_call}, all_data={all_data}, save_to_jsonl={save_to_jsonl}')
    
    try:
        # Use q as alias for qty if provided
        actual_qty = q if q is not None else qty
        
        # If all_data is True, override other flags to include everything
        if all_data:
            logger.debug('all_data=True: Overriding flags to include comprehensive data')
            always_cpf = True
            always_pis = True
            always_cnpj = True
            always_cei = True
            always_rg = True
            always_phone = True
            always_middle = True
            only_cpf = False
            only_pis = False
            only_cnpj = False
            only_cei = False
            only_rg = False
            only_fone = False
            only_surname = False
            only_middle = False
            only_cep = False
            city_only = False
            state_abbr_only = False
            state_full_only = False
            return_only_name = False
            only_document = False
        
        # Initialize samplers
        logger.debug('Initializing samplers')
        doc_sampler = DocumentSampler()
        location_sampler = BrazilianLocationSampler(json_path)
        
        # Load location data if provided
        if locations_path:
            try:
                with Path(locations_path).open(encoding='utf-8') as f:
                    locations_data = json.load(f)
                    # Use locations data if available
                    if 'cities' in locations_data:
                        location_sampler.update_cities(locations_data['cities'])
                    if 'states' in locations_data:
                        location_sampler.update_states(locations_data['states'])
            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                logger.warning(f'Could not use locations_path data: {e}')
        
        # Load names data
        with Path(surnames_path).open(encoding='utf-8') as f:
            surnames_data = json.load(f)
        
        name_data = {'surnames': surnames_data['surnames']}
        if names_path:
            with Path(names_path).open(encoding='utf-8') as f:
                names_data = json.load(f)
                name_data.update(names_data)
        
        name_sampler = BrazilianNameSampler(
            name_data,
            middle_names_path,
            None,  # No need for names_path as we've already loaded it
        )
        
        # Create a list to store our location items
        location_items = []
        
        # Generate the requested number of samples
        for i in range(actual_qty):
            # Generate location information
            state_name, state_abbr, city_name = location_sampler.get_state_and_city()
            cep = location_sampler._get_random_cep_for_city(city_name)
            
            # Format the CEP with or without dash as requested
            formatted_cep = cep
            if not cep_without_dash and len(cep) == 8:
                formatted_cep = f'{cep[:5]}-{cep[5:]}'
            
            # Generate name components
            name_components = None
            if not only_document:
                if only_surname:
                    name_components = NameComponents(
                        '', None, name_sampler.get_random_surname(top_40=top_40, raw=name_raw, with_only_one_surname=with_only_one_surname)
                    )
                elif only_middle:
                    name_components = name_sampler.get_random_name(raw=name_raw, only_middle=True, return_components=True)
                else:
                    name_components = name_sampler.get_random_name(
                        time_period=time_period,
                        raw=name_raw,
                        include_surname=True,
                        top_40=top_40,
                        with_only_one_surname=with_only_one_surname,
                        always_middle=always_middle,
                        return_components=True,
                    )
            
            # Generate a new location item
            location_item = LocationItem(
                cep=formatted_cep,
                city_name=city_name,
                city_uf=state_abbr,
                state=state_name,
            )
            
            # Add name information if available
            if name_components:
                location_item.name = name_components.first_name
                location_item.middle_name = name_components.middle_name
                location_item.surnames = name_components.surname
            
            # Generate documents as requested
            if always_cpf or only_cpf:
                location_item.cpf = doc_sampler.generate_cpf()
            if always_pis or only_pis:
                location_item.pis = doc_sampler.generate_pis()
            if always_cnpj or only_cnpj:
                location_item.cnpj = doc_sampler.generate_cnpj()
            if always_cei or only_cei:
                location_item.cei = doc_sampler.generate_cei()
            if always_rg or only_rg:
                location_item.rg = f'{doc_sampler.generate_rg(state_abbr, include_issuer)}'
            if always_phone or only_fone:
                # Get the DDD from the city data
                city_data = location_sampler.get_city_data_by_name(city_name, state_abbr)
                ddd = city_data.get('ddd')
                if ddd:
                    location_item.phone = generate_phone_number(ddd)
                else:
                    logger.warning(f"No DDD found for city {city_name}, {state_abbr}. Cannot generate phone number.")
            
            # Add the location item to our list
            location_items.append(location_item)
            
            # Report progress if callback is provided
            if progress_callback and i % max(1, actual_qty // 10) == 0:
                await progress_callback(i + 1, f'Generated {i+1}/{actual_qty} items')
        
        # Process the location items to add address data and save results
        if make_api_call or save_to_jsonl:
            processed_items = await process_and_save_in_batches(
                location_items,
                make_api_call,
                save_to_jsonl,
                append_to_jsonl,
                progress_callback,
                batch_size=batch_size,  # Use provided batch_size
                num_workers=num_workers  # Use provided num_workers
            )
            
            # Update progress if callback is provided
            if progress_callback:
                await progress_callback(actual_qty, 'Completed')
            
            # Return a single item or the whole list based on qty
            return processed_items[0] if actual_qty == 1 else processed_items
        else:
            # If no API calls or saving needed, just return the items as is
            return location_items[0] if actual_qty == 1 else location_items
    
    except Exception as e:
        logger.error(f'Error generating samples: {e}')
        raise RuntimeError(f'Error generating samples: {e}') from e


def sample_sync(
    qty: int = 1,
    q: int | None = None,
    city_only: bool = False,
    state_abbr_only: bool = False,
    state_full_only: bool = False,
    only_cep: bool = False,
    cep_without_dash: bool = False,
    make_api_call: bool = False,
    time_period: TimePeriod = TimePeriod.UNTIL_2010,
    return_only_name: bool = False,
    name_raw: bool = False,
    json_path: str | Path = Path(__file__).parent / 'data' / 'location_data.json',
    names_path: str | Path = Path(__file__).parent / 'data' / 'names_data.json',
    middle_names_path: str | Path = Path(__file__).parent / 'data' / 'middle_names.json',
    only_surname: bool = False,
    top_40: bool = False,
    with_only_one_surname: bool = False,
    always_middle: bool = False,
    only_middle: bool = False,
    always_cpf: bool = False,
    always_pis: bool = False,
    always_cnpj: bool = False,
    always_cei: bool = False,
    always_rg: bool = False,
    always_phone: bool = False,
    only_cpf: bool = False,
    only_pis: bool = False,
    only_cnpj: bool = False,
    only_cei: bool = False,
    only_rg: bool = False,
    only_fone: bool = False,
    include_issuer: bool = False,
    only_document: bool = False,
    surnames_path: str | Path = Path(__file__).parent / 'data' / 'surnames_data.json',
    locations_path: str | Path = '',
    save_to_jsonl: str | None = None,
    all_data: bool = False,
    progress_callback: callable = None,
    append_to_jsonl: bool = True,
    batch_size: int = 100,
    num_workers: int = 100,
) -> List[LocationItem] | LocationItem:
    """Synchronous wrapper for the async sample function.
    
    This provides backward compatibility for code that expects a synchronous function.
    All parameters are passed directly to the async sample function.
    """
    return asyncio.run(sample(
        qty=qty,
        q=q,
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
        batch_size=batch_size,
        num_workers=num_workers,
    ))
