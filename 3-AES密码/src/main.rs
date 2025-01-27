use std::vec::Vec;

use colored::*;

const AES_BLOCK_SIZE: usize = 16;

fn xor_block(block: &mut [u8], iv: &[u8]) {
    for i in 0..AES_BLOCK_SIZE {
        block[i] ^= iv[i];
    }
}

fn aes_encrypt_block(block: &mut [u8], key: &[u8; AES_BLOCK_SIZE]) {
    // test encryption
    for i in 0..AES_BLOCK_SIZE {
        block[i] = block[i] ^ key[i];
    }
}

fn aes_decrypt_block(block: &mut [u8], key: &[u8; AES_BLOCK_SIZE]) {
    // test decryption
    aes_encrypt_block(block, key);
}

fn pkcs7_padding(data: &[u8]) -> Vec<u8> {
    let pad_len = (AES_BLOCK_SIZE - (data.len() % AES_BLOCK_SIZE)) % AES_BLOCK_SIZE;
    let mut padded_data = data.to_vec();
    padded_data.extend(vec![pad_len as u8; pad_len]);
    padded_data
}

fn aes_cbc_encrypt(key: &[u8; AES_BLOCK_SIZE], iv: &[u8; AES_BLOCK_SIZE], data: &[u8]) -> Vec<u8> {
    let mut encrypted_data = Vec::new();
    let mut prev_block = iv.to_vec();

    let mut padded_data = pkcs7_padding(data);

    for chunk in padded_data.chunks_mut(AES_BLOCK_SIZE) {
        xor_block(chunk, &prev_block); // xor with prev chunk
        aes_encrypt_block(chunk, key); // encrypt
        encrypted_data.extend_from_slice(chunk); // extend cur chunk
        prev_block.copy_from_slice(chunk); // update prev chunk (for next iteration)
    }
    encrypted_data
}

fn aes_cbc_decrypt(key: &[u8; AES_BLOCK_SIZE], iv: &[u8; AES_BLOCK_SIZE], data: &[u8]) -> Vec<u8> {
    let mut decrypted_data = Vec::new();
    let mut prev_block = iv.to_vec();

    for chunk in data.to_vec().chunks_exact_mut(AES_BLOCK_SIZE) {
        let cipher_chunk = chunk.to_vec();
        aes_decrypt_block(chunk, key); // decrypt
        xor_block(chunk, &prev_block); // xor with prev chunk
        decrypted_data.extend_from_slice(chunk); // extend cur chunk
        prev_block.copy_from_slice(&cipher_chunk); // update prev chunk with the cipher (for next iteration)
    }
    decrypted_data
}

trait AesString {
    fn parse_hex(&self) -> Vec<u8>;
}

impl AesString for str {
    fn parse_hex(&self) -> Vec<u8> {
        self.as_bytes()
            .chunks(2)
            .map(|b| u8::from_str_radix(std::str::from_utf8(b).unwrap(), 16).unwrap())
            .collect()
    }
}

trait AesVec {
    fn to_string(&self) -> String;
    fn to_hex(&self) -> String;
}

impl AesVec for Vec<u8> {
    fn to_string(&self) -> String {
        String::from_utf8(self.clone()).unwrap()
    }
    fn to_hex(&self) -> String {
        self.iter()
            .map(|b| format!("{:02x}", b))
            .collect::<Vec<String>>()
            .join("")
    }
}

fn main() {
    let key: [u8; AES_BLOCK_SIZE] = [
        0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x97, 0x75, 0x46, 0x73, 0x0a,
        0x09,
    ];

    let iv: [u8; AES_BLOCK_SIZE] = [0x00; AES_BLOCK_SIZE];

    let data = b"Hello, this is a test message!!!.";

    let encrypted_data = &aes_cbc_encrypt(&key, &iv, &data.to_vec()).to_hex();
    println!("{} {}", "Encrypt:".cyan(), encrypted_data);

    let decrypted_data = aes_cbc_decrypt(&key, &iv, &encrypted_data.parse_hex()).to_string();
    println!("{} {}", "Decrypt:".cyan(), &decrypted_data);
}
