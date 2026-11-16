import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ouroboros import OuroborosEngine

print("=== OUROBOROS INTERAKTIV TESZT ===")
szoveg = input("Irj be egy rovid uzenetet (pl. Szia vilag 2026): ")
adat = szoveg.encode("utf-8")

# 1. RAW_FAST + Hibajavitas teszt
iot = OuroborosEngine(mode="RAW_FAST")
kodolt = iot.encode_data(adat)
print("\n[1] RAW_FAST kodolt kimenet:")
print("   ", " ".join(kodolt))

# Szandekosan elrontunk egy maganhangzot az elso blokkban!
hibas_kodolt = list(kodolt)
elso_blokk = list(hibas_kodolt[0])
for i in range(4):
    if elso_blokk[i] in "aeio":
        elso_blokk[i] = "o" if elso_blokk[i] != "o" else "a"
        break
hibas_kodolt[0] = "".join(elso_blokk)

print("\n[2] Szandekosan elrontott elso blokk (zaj szimulacio):")
print("   ", " ".join(hibas_kodolt))

visszafejtett, javitott_db = iot.decode_data(hibas_kodolt, original_length=len(adat))
print(f"\n[3] Visszafejtve: '{visszafejtett.decode('utf-8')}' (Javitott blokkok: {javitott_db})")

# 2. STEGO_PROSE + Titkos kulcs (Seed) teszt
kulcs = input("\nAdj meg egy titkos kulcsot az alcazashoz (pl. titok123): ")
stego = OuroborosEngine(mode="STEGO_PROSE", seed=kulcs)
alcazott = stego.encode_data(adat)
print("\n[4] Alcazott halozati forgalom (STEGO_PROSE):")
print("   ", " | ".join(alcazott))

vissza_stego, _ = stego.decode_data(alcazott, original_length=len(adat))
print("\n[5] Visszafejtve a kulccsal:", vissza_stego.decode("utf-8"))
