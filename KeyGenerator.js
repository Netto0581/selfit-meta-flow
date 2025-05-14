/**
 * Copyright (c) Meta Platforms, Inc. and affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

/* The script will generate a public and private key pair and log the same in the console.
 * Copy paste the private key into your /.env file and public key should be added to your account.
 * For more details visit: https://developers.facebook.com/docs/whatsapp/flows/guides/implementingyourflowendpoint#upload_public_key
 *
 * Run this script using command below:
 *
 *             node src/keyGenerator.js {passphrase}
 *
 */

const crypto = require('crypto');

class KeyGenerator {
    static generateKey() {
        // Gera uma chave aleatória de 32 bytes
        const key = crypto.randomBytes(32);
        return key.toString('base64');
    }

    static validateKey(key) {
        try {
            // Verifica se a chave é uma string base64 válida
            const buffer = Buffer.from(key, 'base64');
            return buffer.length === 32;
        } catch (error) {
            return false;
        }
    }

    static formatKey(key) {
        // Formata a chave no formato esperado pelo Meta
        return `EAA${key}`;
    }
}

module.exports = KeyGenerator;
