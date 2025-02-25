import asyncio
import json
import subprocess
import sys
from typing import Any


async def get_cep_data(cep: str) -> dict[str, Any]:
    """
    Retrieves address information for a single CEP using cep_service.js
    which directly imports from the cep-promise package.

    Args:
        cep: A CEP (string).

    Returns:
        A dictionary containing the address information.
        Returns an error dictionary if there is an issue after 100 retry attempts.
    """
    # Ensure cep is a string
    cep = str(cep)

    max_retries = 100
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Use the cep_service.js directly
            process = await asyncio.create_subprocess_exec(
                'node',
                'src/utils/cep_service.js',
                cep,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_output = stderr.decode('utf-8').strip() if stderr else 'No error details available'
                retry_count += 1
                if retry_count >= max_retries:
                    return {'error': f'Error calling cep_service.js after {max_retries} retries: {error_output}', 'cep': cep}
                await asyncio.sleep(0.01)  # Small delay between retries
                continue  # Skip to next iteration

            result = json.loads(stdout.decode('utf-8'))

            # If result is a list with one item, return that item
            if isinstance(result, list) and len(result) == 1:
                return result[0]
            return result

        except subprocess.CalledProcessError as e:
            retry_count += 1
            if retry_count >= max_retries:
                return {'error': f'Error calling cep_service.js after {max_retries} retries: {e}', 'cep': cep}
            await asyncio.sleep(0.01)  # Small delay between retries

        except json.JSONDecodeError as e:
            retry_count += 1
            if retry_count >= max_retries:
                return {'error': f'Error decoding JSON after {max_retries} retries: {e}', 'cep': cep}
            await asyncio.sleep(0.01)  # Small delay between retries

        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                return {'error': f'Unexpected error after {max_retries} retries: {e!s}', 'cep': cep}
            await asyncio.sleep(0.01)  # Small delay between retries


async def workers_for_multiple_cep(ceps: list[str], max_workers: int = 10) -> list[dict[str, Any]]:
    """
    Process multiple CEPs concurrently using a worker pool.

    Args:
        ceps: List of CEP strings to process
        max_workers: Maximum number of concurrent workers

    Returns:
        List of dictionaries containing address information for each CEP
    """
    # Use worker pool approach for individual processing
    queue = asyncio.Queue()

    # Add all CEPs to the queue
    for cep in ceps:
        await queue.put(cep)

    # Results container with mapping to preserve order
    results_dict = {}

    # Worker function that processes CEPs from the queue
    async def worker():
        while not queue.empty():
            try:
                # Get a CEP from the queue
                cep = await queue.get()

                # Process the CEP using get_cep_data function
                result = await get_cep_data(cep)

                # Store the result with the CEP as key to preserve order
                results_dict[cep] = result

                # Mark task as done
                queue.task_done()
            except Exception as e:
                # Handle any exceptions in the worker
                results_dict[cep] = {'error': f'Worker error processing CEP: {e!s}', 'cep': cep}
                queue.task_done()

    # Create worker tasks
    tasks = []
    for _ in range(min(max_workers, len(ceps))):
        task = asyncio.create_task(worker())
        tasks.append(task)

    # Wait for the queue to be fully processed
    await queue.join()

    # Cancel any remaining worker tasks
    for task in tasks:
        task.cancel()

    # Wait for all tasks to be cancelled
    await asyncio.gather(*tasks, return_exceptions=True)

    # Convert results dict back to list in the original order
    return [results_dict.get(cep, {'error': 'CEP processing failed', 'cep': cep}) for cep in ceps]


async def display_cep_info(data):
    """Display CEP information in a formatted way."""
    if isinstance(data, list):
        for cep_info in data:
            if 'error' in cep_info:
                print(f'Error: {cep_info["error"]}')
            else:
                print(f'CEP: {cep_info.get("cep", "N/A")}')
                print(f'State: {cep_info.get("state", "N/A")}')
                print(f'City: {cep_info.get("city", "N/A")}')
                print(f'Neighborhood: {cep_info.get("neighborhood", "N/A")}')
                print(f'Street: {cep_info.get("street", "N/A")}')
                print(f'Service: {cep_info.get("service", "N/A")}')
                print()
    else:
        if 'error' in data:
            print(f'Error: {data["error"]}')
        else:
            print(f'CEP: {data.get("cep", "N/A")}')
            print(f'State: {data.get("state", "N/A")}')
            print(f'City: {data.get("city", "N/A")}')
            print(f'Neighborhood: {data.get("neighborhood", "N/A")}')
            print(f'Street: {data.get("street", "N/A")}')
            print(f'Service: {data.get("service", "N/A")}')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ceps = sys.argv[1:]

        async def main():
            # If there's only one CEP, use get_cep_data directly
            if len(ceps) == 1:
                data = await get_cep_data(ceps[0])
                await display_cep_info(data)
            # Otherwise use the worker pool for multiple CEPs
            else:
                data = await workers_for_multiple_cep(ceps)
                await display_cep_info(data)

        asyncio.run(main())
