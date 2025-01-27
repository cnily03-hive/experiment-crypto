use clap::arg;
use clap::{ArgAction, ArgGroup, Command};

mod utils;

mod vigenere;
mod hill;

fn main() {
    let m = Command::new("GuDian")
        .version("1.0")
        .author("Cnily03")
        .about("Course design for crypto course")
        .subcommand(
            // vigenere
            Command::new("vigenere")
                .aliases(&["vig", "vg"])
                .arg(arg!(file: <FILE> "The file to encrypt/decrypt").group("method"))
                .args(&[
                    arg!(enc: -e --encrypt "Encrypt the plaintext")
                        .required(true)
                        .action(ArgAction::SetTrue),
                    arg!(dec: -d --decrypt "Decrypt the ciphertext")
                        .required(true)
                        .action(ArgAction::SetTrue),
                ])
                .args(&[
                    arg!(key: -K --key <KEY> "The key for encryption/decryption")
                        .required(true)
                        .value_parser(vigenere::assert_key),
                    arg!(stdin: -i --stdin "Read the plaintext/ciphertext from stdin")
                        .required(true)
                        .group("method"),
                ])
                .group(ArgGroup::new("operation").args(&["enc", "dec"])),
        )
        .subcommand(
            // hill
            Command::new("hill")
                .aliases(&["hl"])
                .arg(arg!(file: <FILE> "The file to encrypt/decrypt").group("method"))
                .args(&[
                    arg!(enc: -e --encrypt "Encrypt the plaintext")
                        .required(true)
                        .action(ArgAction::SetTrue),
                    arg!(dec: -d --decrypt "Decrypt the ciphertext")
                        .required(true)
                        .action(ArgAction::SetTrue),
                ])
                .args(&[
                    arg!(key: -K --key <KEY> "The key for encryption/decryption, number split by comma or space, or whole alphabetic")
                        .required(true)
                        .value_parser(hill::assert_key),
                    arg!(size: -s --size <SIZE> "The size of the key matrix")
                        .required(true)
                        .value_parser(hill::assert_size),
                    arg!(stdin: -i --stdin "Read the plaintext/ciphertext from stdin")
                        .required(true)
                        .group("method"),
                ])
                .group(ArgGroup::new("operation").args(&["enc", "dec"])),
        )
        .get_matches();

    match m.subcommand_name() {
        Some("vigenere") => vigenere::command_entry(m.subcommand_matches("vigenere").unwrap()),
        Some("hill") => hill::command_entry(m.subcommand_matches("hill").unwrap()),
        _ => {}
    }
}
