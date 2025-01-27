use crate::utils;

fn encrypt(plaintext: &str, key: &str) -> String {
    let key = key.chars().cycle();
    let mut ciphertext = String::new();

    for (p, k) in plaintext.chars().zip(key) {
        // only alpha
        if p.is_alphabetic() {
            let base = if p.is_lowercase() { 'a' } else { 'A' };
            let p_offset = utils::delta_char(p);
            let k_offset = k.to_ascii_lowercase() as u8 - 'a' as u8;
            let encrypted_char = ((p_offset + k_offset) % 26) + base as u8;
            ciphertext.push(encrypted_char as char);
        } else {
            ciphertext.push(p); // push non-alpha
        }
    }

    ciphertext
}

fn decrypt(ciphertext: &str, key: &str) -> String {
    let key = key.chars().cycle();
    let mut plaintext = String::new();

    for (c, k) in ciphertext.chars().zip(key) {
        // only alpha
        if c.is_alphabetic() {
            let base = if c.is_lowercase() { 'a' } else { 'A' };
            let c_offset = c.to_ascii_lowercase() as u8 - 'a' as u8;
            let k_offset = k.to_ascii_lowercase() as u8 - 'a' as u8;
            let decrypted_char = ((c_offset + 26 - k_offset) % 26) + base as u8;
            plaintext.push(decrypted_char as char);
        } else {
            plaintext.push(c); // non-alpha
        }
    }

    plaintext
}

pub fn command_entry(m: &clap::ArgMatches) {
    assert!(m.contains_id("operation"));
    let is_enc = m.get_flag("enc");
    let cipherkey = m.get_one::<String>("key").unwrap();

    let buffer = utils::get_buffer(&m);

    if is_enc {
        let ciphertext = encrypt(&buffer, &cipherkey);
        print!("{}", ciphertext);
    } else {
        let plaintext = decrypt(&buffer, &cipherkey);
        print!("{}", plaintext);
    }
}

pub fn assert_key(key: &str) -> Result<String, String> {
    if key.chars().all(|c| c.is_alphabetic()) {
        Ok(key.to_string())
    } else {
        Err("The key must be alphabetic".to_string())
    }
}
