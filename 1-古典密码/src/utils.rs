use std::io::Read;

pub fn delta_char(c: char) -> u8 {
    c.to_ascii_uppercase() as u8 - 'A' as u8
}

pub fn char_from_delta(d: u8, upper: bool) -> char {
    (d + (if upper { 'A' as u8 } else { 'a' as u8 })) as char
}

/// Reads input from either standard input or a file specified in the command line arguments.
/// The `stdin` flag and the `file` flag must exist in the command line arguments.
pub fn get_buffer(m: &clap::ArgMatches) -> String {
    let enable_stdin = m.get_flag("stdin");
    if enable_stdin {
        let mut buffer = String::new();
        std::io::stdin().read_to_string(&mut buffer).unwrap();
        buffer
    } else {
        let fp = m.get_one::<String>("file").unwrap();
        // throw warning: file not found
        match std::fs::read_to_string(fp) {
            Ok(buffer) => buffer,
            Err(e) => error_handle::io(e),
        }
    }
}

pub mod error_handle {

    use colored::*;
    use std::io;

    pub fn io<T>(e: io::Error) -> T {
        match e.kind() {
            io::ErrorKind::NotFound => {
                eprintln!("{} {}", "error:".red().bold(), "File not found");
                std::process::exit(1);
            }
            io::ErrorKind::PermissionDenied => {
                eprintln!("{} {}", "error:".red().bold(), "Permission denied");
                std::process::exit(1);
            }
            _ => {
                eprintln!("{} {}", "error:".red().bold(), e);
                std::process::exit(1);
            }
        }
    }

    pub fn string<T>(e: String) -> T {
        eprintln!("{} {}", "error:".red().bold(), e);
        std::process::exit(1);
    }

}