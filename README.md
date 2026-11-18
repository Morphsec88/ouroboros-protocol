# Ouroboros Protocol

**A zero-dependency, deterministic cyclic encoding framework with built-in 3-vs-1 filler error correction, LLM-safe word framing, and dynamic morphological steganography.**

[![License: AGPL v3](https://shields.io)](https://gnu.org)
[![Zero Dependencies](https://shields.io)]()
[![C99 & Python](https://shields.io)]()

---

## Core Concept (Tail-Chasing Cyclic Engine)

Inspired by the ancient symbol of the **Ouroboros**, the protocol maps every single byte (`8 bits`) into a **4-element cyclic ring** using pure bitwise shifts and masks:

```text
  1 Byte (8 bits):  [ C3 C2 C1 C0 ]  [ P1 P0 ]  [ F1 F0 ]
                     └─── Core ───┘   └─ Pos ─┘  └Filler─┘
                      (16 options)    (0..3)     (4 options)

  4-Element Cyclic Block (Example: Core='g', Pos=2, Filler='a'):
  ┌─────────┬─────────┬─────────┬─────────┐
  │   'a'   │   'a'   │   'g'   │   'a'   │  ──▶ Self-healing 3-vs-1 filler vote
  └─────────┴─────────┴─────────┴─────────┘
```

* **Built-in Filler Recovery (3-vs-1 FEC):** Because the 3 filler slots carry identical values, any single filler corruption caused by channel noise is automatically repaired via a **3-vs-1 majority vote**—requiring zero external checksums or retransmissions. *(Note: This mechanism protects the redundant filler slots; direct corruption of the single core element is detected and flagged rather than auto-repaired).*
* **Dynamic Mutation (`seed` mode):** When initialized with a secret seed (available in the Python engine), the lookup tables cyclically rotate after every processed byte, turning plain text into deterministic, morphing word sequences for steganographic obfuscation.

> **Security Notice:** The `seed` mode provides **keyed obfuscation and steganography**, not cryptographic encryption. Do not use it alone to protect confidential data; always encrypt sensitive payloads (e.g., using AES-GCM or ChaCha20) prior to encoding.

---

## Three Modes, One Bitwise Engine

| Mode | Target Sector | Alphabet / Vocabulary | Key Advantage |
| :--- | :--- | :--- | :--- |
| **`RAW_FAST`** | IoT, LoRa, Satellites, MCUs | 16 Consonants + 4 Vowels | Hardware-speed bitwise ops (`c_core/ouroboros.h`), zero `malloc`, automatic single-filler recovery. |
| **`LLM_TOKEN`** | AI Agents & LLM Pipelines | Single-token English words | Avoids punctuation and special-character parsing issues by framing binary data into clean, predictable single-token words. |
| **`STEGO_PROSE`** | Traffic Obfuscation & Logs | System telemetry vocabulary | Disguises binary payloads as harmless server status logs (`"active thread active active"`). |

---

## Verified Benchmark Results

Tested against standard Base64 under a simulated **25% single-filler corruption rate** (where up to 1 filler character per 4-char block is altered):

```text
[2] SELF-HEALING / FAULT TOLERANCE TEST (25% single-filler noise)
  Base64 survived noise?      : False (Corrupted or crashed)
  Ouroboros survived noise?   : True (100% data recovery!)
  Errors auto-repaired (FEC)  : 224 blocks healed without retransmission

[3] DYNAMIC MUTATION (SEEDED STEGO_PROSE)
  Sample intercepted traffic  : 'active thread active active active active active thread'
  Decoded with valid seed     : True -> TELEMETRY_PAYLOAD_2026
  Decoded with wrong seed     : False (Blocked immediately by cyclic check)
```

---

## Quick Start (Python)

### Installation
```bash
git clone https://github.com
cd ouroboros-protocol
pip install .
```

### Usage Example
```python
from ouroboros import OuroborosEngine

# 1. IoT / Noise-Resistant Mode
iot = OuroborosEngine(mode="RAW_FAST")
encoded = iot.encode_data(b"OK")
decoded, repaired = iot.decode_data(encoded, original_length=2)

# 2. Seeded Steganography Mode (Obfuscation)
stego = OuroborosEngine(mode="STEGO_PROSE", seed="MySecretKey2026")
hidden_traffic = stego.encode_data(b"TELEMETRY_PAYLOAD_2026")
print(hidden_traffic)
```

---

## Embedded C99 / Hardware Integration

For microcontrollers (ESP32, STM32, Arduino) or ASIC/FPGA synthesis, include the single-header library `c_core/ouroboros.h`. It implements the **`RAW_FAST` mode** using **zero dynamic memory (`malloc`)** and compiles cleanly on any C99/C++ compiler. See `examples/iot_lora.ino` for a full wireless telemetry demo.

---

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)** — see the `LICENSE` file for details. Commercial dual-licensing is available upon request.
