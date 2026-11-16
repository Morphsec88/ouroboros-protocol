# Ouroboros Protocol

**A zero-dependency, deterministic cyclic encoding framework with built-in 3-vs-1 Forward Error Correction (FEC), LLM token optimization, and dynamic morphological steganography.**

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
  │   'a'   │   'a'   │   'g'   │   'a'   │  ──▶ Self-healing 3-vs-1 vote
  └─────────┴─────────┴─────────┴─────────┘
```

* **Built-in Self-Healing (FEC):** Because the 3 filler slots carry identical values, any single filler corruption caused by radio noise or packet bit-flips is automatically repaired via a **3-vs-1 majority vote**—requiring zero external checksums or retransmissions.
* **Dynamic Mutation (`seed` mode):** When initialized with a secret seed, the lookup tables cyclically rotate after every processed byte, turning plain text or radio signals into a self-mutating stream cipher.

---

## Three Modes, One Bitwise Engine

| Mode | Target Sector | Alphabet / Vocabulary | Key Advantage |
| :--- | :--- | :--- | :--- |
| **`RAW_FAST`** | IoT, LoRa, Satellites, MCUs | 16 Consonants + 4 Vowels | Hardware-speed bitwise ops (`c_core/ouroboros.h`), zero `malloc`, survives heavy RF noise. |
| **`LLM_TOKEN`** | AI Agents & LLM Pipelines | Single-token English words | Eliminates Base64 token fragmentation when passing binary payloads between AI agents. |
| **`STEGO_PROSE`** | Cybersecurity & Firewalls | System telemetry vocabulary | Disguises binary payloads as harmless server status logs (`"active thread active active"`). |

---

## Verified Benchmark Results

Tested against standard Base64 on a 25% block-noise channel:

```text
[2] SELF-HEALING / FAULT TOLERANCE TEST (25% block noise)
  Base64 survived noise?      : False (Corrupted or crashed)
  Ouroboros survived noise?   : True (100% data recovery!)
  Errors auto-repaired (FEC)  : 224 blocks healed without retransmission

[3] DYNAMIC MUTATION (SEEDED STEGO_PROSE)
  Sample intercepted traffic  : 'active thread active active active active active thread'
  Decrypted with valid seed   : True -> TOP_SECRET_AGENT_PAYLOAD_2026
  Decrypted with wrong seed   : False (Blocked immediately by cyclic check)
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

# 2. Seeded Steganography Mode
stego = OuroborosEngine(mode="STEGO_PROSE", seed="MySecretKey2026")
hidden_traffic = stego.encode_data(b"LAUNCH_CODES")
print(hidden_traffic)
```
### Running the Benchmarks & Interactive Demo
After cloning the repository, you can run the built-in test suites directly from your terminal:

```bash
# Run speed, noise-tolerance, and steganography benchmarks
python examples/benchmark.py

# Launch the interactive CLI playground
python examples/play.py
```

---

## Embedded C99 / Hardware Integration

For microcontrollers (ESP32, STM32, Arduino) or ASIC/FPGA synthesis, include the single-header library `c_core/ouroboros.h`. It uses **zero dynamic memory (`malloc`)** and compiles cleanly on any C99/C++ compiler. See `examples/iot_lora.ino` for a full wireless telemetry demo.

---

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)** — see the `LICENSE` file for details. Commercial dual-licensing is available upon request.
Copyright (c) 2026 Morphsec88 (Istvan Fejes). All rights reserved under the AGPL-3.0 license.
