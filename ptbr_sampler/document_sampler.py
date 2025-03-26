"""Brazilian document number generator using utility functions."""

from ptbr_sampler.br_rg_class import BrazilianRG
from ptbr_sampler.utils.cei import random_cei
from ptbr_sampler.utils.cnpj import random_cnpj
from ptbr_sampler.utils.cpf import random_cpf
from ptbr_sampler.utils.pis import random_pis


class DocumentSampler:
    """Class for generating various Brazilian documents."""

    def __init__(self, only_rg: bool = False):
        """Initialize the document sampler."""
        self.rg_generator = BrazilianRG(only_rg=only_rg)

    def generate_cpf(self, formatted: bool = True) -> str:
        """Generate a valid CPF number.

        Args:
            formatted: If True, returns CPF in XXX.XXX.XXX-XX format
        """
        return random_cpf(formatted=formatted)

    def generate_pis(self, formatted: bool = True) -> str:
        """Generate a valid PIS number.

        Args:
            formatted: If True, returns PIS in XXX.XXXXX.XX-X format
        """
        return random_pis(formatted=formatted)

    def generate_cnpj(self, formatted: bool = True) -> str:
        """Generate a valid CNPJ number.

        Args:
            formatted: If True, returns CNPJ in XX.XXX.XXX/XXXX-XX format
        """
        return random_cnpj(formatted=formatted)

    def generate_cei(self, formatted: bool = True) -> str:
        """Generate a valid CEI number.

        Args:
            formatted: If True, returns CEI in XX.XXX.XXXXX/XX format
        """
        return random_cei(formatted=formatted)

    def generate_rg(self, state: str | None = None, include_issuer: bool = True, only_rg: bool = False) -> str:
        """Generate a valid RG number for the given state.

        Args:
            state: Two-letter state abbreviation (e.g., 'SP', 'RJ')
            formatted: If True, returns RG in XX.XXX.XXX-X format
            only_rg: If True, returns only the RG number
        """
        return self.rg_generator.generate(state=state, include_issuer=include_issuer, only_rg=only_rg)
