import hashlib
import random
from collections import Counter

# 1. PROFILES DEFINITION (3 MODES, 1 ENGINE)
PROFILES = {
    # Mode 1: Ultra-fast single characters for IoT, LoRa radio, and hardware
    "RAW_FAST": {
        "core": list("bcdfghklmnprstvz"),  # 16 consonants
        "filler": list("aeio"),            # 4 vowels
        "separator": ""
    },
    # Mode 2: Single-token English words optimized for AI/LLM context windows
    "LLM_TOKEN": {
        "core": [
            "system", "data", "node", "link", "code", "byte", "port", "host",
            "path", "file", "task", "sync", "core", "grid", "mesh", "flux"
        ],
        "filler": ["in", "on", "at", "by"],
        "separator": " "
    },
    # Mode 3: Natural prose words for steganography (firewall/filter evasion)
    "STEGO_PROSE": {
        "core": [
            "server", "network", "protocol", "client", "buffer", "packet", "stream", "signal",
            "memory", "kernel", "module", "socket", "thread", "vector", "matrix", "cluster"
        ],
        "filler": ["active", "stable", "ready", "synced"],
        "separator": " "
    }
}


class OuroborosEngine:
    def __init__(self, mode: str = "RAW_FAST", seed: str | None = None):
        if mode not in PROFILES:
            raise ValueError(f"Unknown mode: {mode}. Available: {list(PROFILES.keys())}")
        self.mode = mode
        self.base_core = list(PROFILES[mode]["core"])
        self.base_filler = list(PROFILES[mode]["filler"])
        self.separator = PROFILES[mode]["separator"]
        self.seed = seed

    def _init_tables(self) -> tuple[list[str], list[str]]:
        """Initializes the lookup tables, optionally shuffled by a secret seed."""
        core = list(self.base_core)
        filler = list(self.base_filler)
        if self.seed is not None:
            seed_bytes = hashlib.sha256(self.seed.encode("utf-8")).digest()
            rng = random.Random(int.from_bytes(seed_bytes, "big"))
            rng.shuffle(core)
            rng.shuffle(filler)
        return core, filler

    @staticmethod
    def _mutate_tables(core: list[str], filler: list[str], byte_val: int) -> None:
        """Dynamically rotates the tables based on the processed byte value (Ouroboros tail-chase)."""
        c_shift = ((byte_val >> 4) ^ (byte_val & 0x0F)) % 16
        f_shift = (byte_val ^ (byte_val >> 2)) % 4
        if c_shift:
            core[:] = core[c_shift:] + core[:c_shift]
        if f_shift:
            filler[:] = filler[f_shift:] + filler[:f_shift]

    def encode_byte(self, byte_val: int, core: list[str], filler: list[str]) -> list[str]:
        """Converts a single byte (0-255) into a 4-element cyclic block."""
        if not 0 <= byte_val <= 255:
            raise ValueError("Byte value must be between 0 and 255.")

        core_idx = (byte_val >> 4) & 0x0F   # Upper 4 bits (0..15)
        position = (byte_val >> 2) & 0x03   # Next 2 bits (0..3)
        filler_idx = byte_val & 0x03        # Lower 2 bits (0..3)

        core_elem = core[core_idx]
        filler_elem = filler[filler_idx]

        block = [filler_elem] * 4
        block[position] = core_elem
        return block

    def decode_block(self, block: list[str], core: list[str], filler: list[str]) -> tuple[int, bool]:
        """
        Restores the original byte from a 4-element block with 3-vs-1 majority error correction.
        Returns: (restored_byte, was_error_corrected)
        """
        if len(block) != 4:
            raise ValueError("Block must consist of exactly 4 elements.")

        error_corrected = False
        core_positions = [i for i, item in enumerate(block) if item in core]

        if len(core_positions) == 1:
            position = core_positions[0]
            core_elem = block[position]
            remaining = [item for i, item in enumerate(block) if i != position]

            most_common_filler, count = Counter(remaining).most_common(1)[0]
            if most_common_filler not in filler:
                raise ValueError(f"Invalid filler element in block: {block}")

            if count < 3:
                error_corrected = True

            core_idx = core.index(core_elem)
            filler_idx = filler.index(most_common_filler)

            byte_val = (core_idx << 4) | (position << 2) | filler_idx
            return byte_val, error_corrected

        elif len(core_positions) == 0:
            raise ValueError(f"Critical error: core lost in block: {block}")
        else:
            raise ValueError(f"Multiple core error (ambiguous core): {block}")

    def encode_data(self, data: bytes) -> list[str]:
        """Converts a byte sequence into 8-element cyclic units (2 bytes = 1 unit)."""
        padded = data + (b"\x00" if len(data) % 2 != 0 else b"")
        core, filler = self._init_tables()

        encoded_units = []
        for i in range(0, len(padded), 2):
            b1, b2 = padded[i], padded[i + 1]
            block1 = self.encode_byte(b1, core, filler)
            if self.seed is not None:
                self._mutate_tables(core, filler, b1)

            block2 = self.encode_byte(b2, core, filler)
            if self.seed is not None:
                self._mutate_tables(core, filler, b2)

            unit = self.separator.join(block1 + block2)
            encoded_units.append(unit)
        return encoded_units

    def decode_data(self, encoded_units: list[str], original_length: int | None = None) -> tuple[bytes, int]:
        """
        Restores original bytes from encoded units.
        Returns: (decoded_bytes, total_errors_repaired)
        """
        output = bytearray()
        core, filler = self._init_tables()
        repaired_count = 0

        for unit in encoded_units:
            elements = list(unit) if self.separator == "" else unit.split(self.separator)
            if len(elements) != 8:
                raise ValueError(f"Unit must contain exactly 8 elements: {unit}")

            byte1, corr1 = self.decode_block(elements[:4], core, filler)
            if corr1:
                repaired_count += 1
            if self.seed is not None:
                self._mutate_tables(core, filler, byte1)

            byte2, corr2 = self.decode_block(elements[4:], core, filler)
            if corr2:
                repaired_count += 1
            if self.seed is not None:
                self._mutate_tables(core, filler, byte2)

            output.append(byte1)
            output.append(byte2)

        if original_length is not None:
            output = output[:original_length]
        return bytes(output), repaired_count
