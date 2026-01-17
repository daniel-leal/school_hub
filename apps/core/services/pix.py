"""
PIX Payment Service for generating QR codes and payment strings.
Based on Brazilian Central Bank's PIX EMV specification.
"""

import io
import re
import unicodedata
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

import qrcode


class PixServiceInterface(Protocol):
    """Interface for PIX payment service."""

    def generate_pix_code(
        self,
        amount: Decimal,
        description: str = "",
        transaction_id: str = "",
    ) -> str:
        """Generate a PIX payment code (EMV format)."""
        ...

    def generate_qr_code(
        self,
        amount: Decimal,
        description: str = "",
        transaction_id: str = "",
    ) -> bytes:
        """Generate a QR code image for PIX payment."""
        ...


@dataclass
class PixPayload:
    """PIX payload data structure."""

    pix_key: str
    merchant_name: str
    merchant_city: str
    amount: Decimal | None = None
    description: str = ""
    transaction_id: str = ""


class PixService:
    """
    Service for generating PIX payment codes and QR codes.
    Implements the Brazilian Central Bank's PIX EMV standard.
    """

    # EMV Tag IDs
    PAYLOAD_FORMAT_INDICATOR = "00"
    POINT_OF_INITIATION = "01"
    MERCHANT_ACCOUNT_INFO = "26"
    MERCHANT_CATEGORY_CODE = "52"
    TRANSACTION_CURRENCY = "53"
    TRANSACTION_AMOUNT = "54"
    COUNTRY_CODE = "58"
    MERCHANT_NAME = "59"
    MERCHANT_CITY = "60"
    ADDITIONAL_DATA_FIELD = "62"
    CRC16 = "63"

    # GUI for PIX
    PIX_GUI = "br.gov.bcb.pix"

    def __init__(
        self,
        pix_key: str = "",
        merchant_name: str = "",
        merchant_city: str = "",
    ):
        self.pix_key = pix_key
        self.merchant_name = self._normalize_text(merchant_name, 25)
        self.merchant_city = self._normalize_text(merchant_city, 15)

    def _remove_accents(self, text: str) -> str:
        """Remove accents from text."""
        # Normalize to NFD form (decomposed)
        normalized = unicodedata.normalize("NFD", text)
        # Remove combining characters (accents)
        without_accents = "".join(
            char for char in normalized if unicodedata.category(char) != "Mn"
        )
        return without_accents

    def _normalize_pix_key(self, key: str) -> str:
        """
        Normalize PIX key according to Brazilian Central Bank specifications.

        Supported key types:
        - Email: kept as-is (lowercase)
        - Phone: E.164 format (+5511999887766)
        - CPF: 11 digits only
        - CNPJ: 14 digits only
        - Random key (EVP): UUID format with hyphens
        """
        if not key:
            return ""

        key = key.strip()

        # Email: contains @ - keep as lowercase
        if "@" in key:
            return key.lower()

        # Random key (EVP/UUID): check UUID pattern first
        # UUID format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        uuid_pattern = r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
        if re.match(uuid_pattern, key):
            return key.lower()

        # Check for 32 hex characters (UUID without hyphens)
        hex_only = re.sub(r"[^a-fA-F0-9]", "", key)
        if len(hex_only) == 32 and re.match(r"^[a-fA-F0-9]+$", key):
            return f"{hex_only[:8]}-{hex_only[8:12]}-{hex_only[12:16]}-{hex_only[16:20]}-{hex_only[20:]}".lower()

        # Remove all non-digit characters for analysis
        digits_only = re.sub(r"[^\d]", "", key)
        has_plus = key.startswith("+")

        # CPF pattern: XXX.XXX.XXX-XX (must have formatting to be detected as CPF)
        cpf_formatted_pattern = r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
        if re.match(cpf_formatted_pattern, key) and len(digits_only) == 11:
            return digits_only

        # CNPJ pattern: XX.XXX.XXX/XXXX-XX
        cnpj_pattern = r"^\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}$"
        if re.match(cnpj_pattern, key) and len(digits_only) == 14:
            return digits_only

        # Phone detection:
        # 1. Starts with + (international format)
        # 2. Has parentheses (like (11) or (011))
        # 3. Starts with 55 and has 12-13 digits (BR country code + phone)
        # 4. Has 10-11 digits and looks like BR phone (DDD + number)
        #    - 11 digits: DDD (2) + 9 + 8 digits (mobile)
        #    - 10 digits: DDD (2) + 8 digits (landline)
        has_parentheses = bool(re.search(r"[\(\)]", key))

        # Check if it looks like a Brazilian phone (DDD 11-99 + number starting with 9 for mobile)
        looks_like_br_phone = False
        if len(digits_only) == 11 and digits_only[2] == "9":
            # 11 digits with 9 in position 3 = likely mobile phone (DDD + 9XXXXXXXX)
            ddd = int(digits_only[:2])
            if 11 <= ddd <= 99:
                looks_like_br_phone = True
        elif len(digits_only) == 10:
            # 10 digits = likely landline (DDD + 8 digits)
            ddd = int(digits_only[:2])
            if 11 <= ddd <= 99:
                looks_like_br_phone = True

        is_phone = (
            has_plus
            or has_parentheses
            or (digits_only.startswith("55") and len(digits_only) >= 12)
            or looks_like_br_phone
        )

        if is_phone and digits_only:
            # Normalize phone to E.164 format
            if has_plus or (digits_only.startswith("55") and len(digits_only) >= 12):
                # Already has country code (with or without +)
                return "+" + digits_only
            elif len(digits_only) == 11:
                # DDD (2) + mobile number (9) - add +55
                return "+55" + digits_only
            elif len(digits_only) == 10:
                # DDD (2) + landline (8) - add +55
                return "+55" + digits_only
            else:
                # Unknown format, return with +55
                return "+55" + digits_only

        # CNPJ: exactly 14 digits
        if len(digits_only) == 14:
            return digits_only

        # CPF: exactly 11 digits (only if not detected as phone)
        if len(digits_only) == 11:
            return digits_only

        # Default: return as-is
        return key

    def _normalize_text(self, value: str, max_length: int) -> str:
        """
        Normalize text for PIX fields.
        - Remove accents
        - Keep only alphanumeric and spaces
        - Convert to uppercase
        - Limit length
        """
        if not value:
            return ""

        # Remove accents
        value = self._remove_accents(value)
        # Keep only alphanumeric and spaces
        value = re.sub(r"[^a-zA-Z0-9 ]", "", value)
        # Remove extra spaces
        value = " ".join(value.split())
        # Convert to uppercase and limit length
        return value.upper()[:max_length]

    def _normalize_txid(self, value: str, max_length: int = 25) -> str:
        """
        Normalize transaction ID for PIX.
        - Keep only alphanumeric characters (no spaces, no special chars)
        - Convert to uppercase
        - Limit length
        """
        if not value:
            return "***"

        # Remove accents first
        value = self._remove_accents(value)
        # Keep only alphanumeric (no spaces)
        value = re.sub(r"[^a-zA-Z0-9]", "", value)
        # Convert to uppercase and limit length
        result = value.upper()[:max_length]

        return result if result else "***"

    def _format_emv_field(self, tag: str, value: str) -> str:
        """Format a single EMV field: TAG + LENGTH (2 digits) + VALUE."""
        length = str(len(value)).zfill(2)
        return f"{tag}{length}{value}"

    def _build_merchant_account_info(self, payload: PixPayload) -> str:
        """Build the merchant account information field (tag 26)."""
        # GUI (tag 00) - required
        gui = self._format_emv_field("00", self.PIX_GUI)

        # PIX Key (tag 01) - required, normalized according to key type
        pix_key = self._normalize_pix_key(payload.pix_key or self.pix_key)
        key = self._format_emv_field("01", pix_key)

        content = gui + key

        # Description (tag 02) - optional
        if payload.description:
            description = self._normalize_text(payload.description, 25)
            if description:
                content += self._format_emv_field("02", description)

        return self._format_emv_field(self.MERCHANT_ACCOUNT_INFO, content)

    def _build_additional_data_field(self, payload: PixPayload) -> str:
        """Build the additional data field (tag 62)."""
        # Transaction ID (tag 05)
        txid = self._normalize_txid(payload.transaction_id, 25)
        content = self._format_emv_field("05", txid)
        return self._format_emv_field(self.ADDITIONAL_DATA_FIELD, content)

    def _calculate_crc16(self, payload: str) -> str:
        """
        Calculate CRC16-CCITT-FALSE checksum for PIX.
        Polynomial: 0x1021
        Initial value: 0xFFFF
        """
        # Add CRC placeholder (tag 63 + length 04)
        payload_with_crc = payload + self.CRC16 + "04"
        data = payload_with_crc.encode("utf-8")

        crc = 0xFFFF
        polynomial = 0x1021

        for byte in data:
            crc ^= byte << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ polynomial
                else:
                    crc <<= 1
                crc &= 0xFFFF

        return format(crc, "04X")

    def generate_pix_code(
        self,
        amount: Decimal | None = None,
        description: str = "",
        transaction_id: str = "",
        pix_key: str = "",
    ) -> str:
        """
        Generate a PIX payment code in EMV format.

        Args:
            amount: Payment amount (optional for static QR codes)
            description: Payment description (max 25 chars)
            transaction_id: Unique transaction identifier (max 25 chars, alphanumeric only)
            pix_key: PIX key to use (overrides default)

        Returns:
            EMV-formatted PIX code string (BR Code)
        """
        payload = PixPayload(
            pix_key=pix_key or self.pix_key,
            merchant_name=self.merchant_name,
            merchant_city=self.merchant_city,
            amount=amount,
            description=description,
            transaction_id=transaction_id,
        )

        result = ""

        # 00 - Payload Format Indicator (required, always "01")
        result += self._format_emv_field(self.PAYLOAD_FORMAT_INDICATOR, "01")

        # 01 - Point of Initiation Method (OPTIONAL)
        # "11" = static (reusable), "12" = dynamic (one-time)
        # NOTE: "12" (dynamic) should only be used by registered PSPs.
        # For manually generated PIX codes, we omit this field entirely
        # to ensure maximum compatibility with all bank apps.

        # 26 - Merchant Account Information (PIX specific)
        result += self._build_merchant_account_info(payload)

        # 52 - Merchant Category Code (required, "0000" for generic)
        result += self._format_emv_field(self.MERCHANT_CATEGORY_CODE, "0000")

        # 53 - Transaction Currency (required, "986" for BRL)
        result += self._format_emv_field(self.TRANSACTION_CURRENCY, "986")

        # 54 - Transaction Amount (optional)
        if amount is not None and amount > 0:
            amount_str = f"{amount:.2f}"
            result += self._format_emv_field(self.TRANSACTION_AMOUNT, amount_str)

        # 58 - Country Code (required, "BR")
        result += self._format_emv_field(self.COUNTRY_CODE, "BR")

        # 59 - Merchant Name (required)
        merchant_name = payload.merchant_name or self.merchant_name or "PAGAMENTO"
        result += self._format_emv_field(self.MERCHANT_NAME, merchant_name)

        # 60 - Merchant City (required)
        merchant_city = payload.merchant_city or self.merchant_city or "BRASIL"
        result += self._format_emv_field(self.MERCHANT_CITY, merchant_city)

        # 62 - Additional Data Field (contains txid)
        result += self._build_additional_data_field(payload)

        # 63 - CRC16 checksum (required, must be last)
        crc = self._calculate_crc16(result)
        result += f"{self.CRC16}04{crc}"

        return result

    def generate_qr_code(
        self,
        amount: Decimal | None = None,
        description: str = "",
        transaction_id: str = "",
        pix_key: str = "",
    ) -> bytes:
        """
        Generate a QR code image for PIX payment.

        Args:
            amount: Payment amount
            description: Payment description
            transaction_id: Unique transaction identifier
            pix_key: PIX key to use (overrides default)

        Returns:
            PNG image bytes
        """
        pix_code = self.generate_pix_code(
            amount=amount,
            description=description,
            transaction_id=transaction_id,
            pix_key=pix_key,
        )

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(pix_code)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer.getvalue()
