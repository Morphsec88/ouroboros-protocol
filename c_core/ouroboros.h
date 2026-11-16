#ifndef OUROBOROS_H
#define OUROBOROS_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* RAW_FAST Character Sets (16 Core Consonants + 4 Filler Vowels) */
static const char OURO_CORE[16] = {
    'b','c','d','f','g','h','k','l','m','n','p','r','s','t','v','z'
};

static const char OURO_FILLER[4] = {
    'a','e','i','o'
};

/* Helper: Returns 0..15 if char is in OURO_CORE, otherwise -1 */
static inline int8_t ouro_find_core(char c) {
    for (int8_t i = 0; i < 16; i++) {
        if (OURO_CORE[i] == c) return i;
    }
    return -1;
}

/* Helper: Returns 0..3 if char is in OURO_FILLER, otherwise -1 */
static inline int8_t ouro_find_filler(char c) {
    for (int8_t i = 0; i < 4; i++) {
        if (OURO_FILLER[i] == c) return i;
    }
    return -1;
}

/**
 * Encodes a single byte into a 4-character cyclic block (RAW_FAST mode).
 * out_block must have space for at least 4 bytes.
 */
static inline void ouro_encode_byte(uint8_t byte_val, char out_block[4]) {
    uint8_t core_idx   = (byte_val >> 4) & 0x0F;
    uint8_t position   = (byte_val >> 2) & 0x03;
    uint8_t filler_idx = byte_val & 0x03;

    char f = OURO_FILLER[filler_idx];
    out_block[0] = f;
    out_block[1] = f;
    out_block[2] = f;
    out_block[3] = f;
    out_block[position] = OURO_CORE[core_idx];
}

/**
 * Decodes a 4-character block back into a byte with 3-vs-1 majority error correction.
 * Returns 0 on success, -1 on unrecoverable core loss, -2 on ambiguous multiple cores.
 */
static inline int ouro_decode_block(const char block[4], uint8_t *out_byte, bool *was_repaired) {
    int8_t core_pos = -1;
    int8_t core_idx = -1;
    uint8_t core_count = 0;

    for (int8_t i = 0; i < 4; i++) {
        int8_t idx = ouro_find_core(block[i]);
        if (idx >= 0) {
            core_pos = i;
            core_idx = idx;
            core_count++;
        }
    }

    if (core_count == 0) return -1; /* Critical error: core lost */
    if (core_count > 1)  return -2; /* Ambiguous core error */

    /* Extract the 3 filler positions and count frequencies (3-vs-1 majority vote) */
    uint8_t counts[4] = {0, 0, 0, 0};
    for (int8_t i = 0; i < 4; i++) {
        if (i == core_pos) continue;
        int8_t f_idx = ouro_find_filler(block[i]);
        if (f_idx >= 0) {
            counts[f_idx]++;
        }
    }

    int8_t best_filler = -1;
    uint8_t max_count = 0;
    for (int8_t f = 0; f < 4; f++) {
        if (counts[f] > max_count) {
            max_count = counts[f];
            best_filler = f;
        }
    }

    if (best_filler < 0 || max_count < 2) {
        return -3; /* Unrecoverable filler corruption */
    }

    if (was_repaired != NULL) {
        *was_repaired = (max_count < 3);
    }

    *out_byte = (uint8_t)((core_idx << 4) | (core_pos << 2) | best_filler);
    return 0;
}

/**
 * Encodes a byte buffer into RAW_FAST cyclic blocks.
 * out_buf must have size >= input_len * 4.
 */
static inline size_t ouro_encode_buffer(const uint8_t *input, size_t input_len, char *out_buf) {
    for (size_t i = 0; i < input_len; i++) {
        ouro_encode_byte(input[i], &out_buf[i * 4]);
    }
    return input_len * 4;
}

/**
 * Decodes a RAW_FAST character buffer back into raw bytes.
 * encoded_len must be a multiple of 4.
 * Returns number of decoded bytes, or 0 on critical error.
 */
static inline size_t ouro_decode_buffer(const char *encoded, size_t encoded_len, uint8_t *out_buf, size_t *repaired_blocks) {
    if (encoded_len % 4 != 0) return 0;
    size_t blocks = encoded_len / 4;
    size_t repairs = 0;

    for (size_t i = 0; i < blocks; i++) {
        bool rep = false;
        if (ouro_decode_block(&encoded[i * 4], &out_buf[i], &rep) != 0) {
            return 0;
        }
        if (rep) repairs++;
    }

    if (repaired_blocks != NULL) {
        *repaired_blocks = repairs;
    }
    return blocks;
}

#ifdef __cplusplus
}
#endif

#endif /* OUROBOROS_H */
