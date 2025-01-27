use nalgebra::DMatrix;
use regex::Regex;
use std::{collections::HashMap, sync::LazyLock};

use crate::utils;

fn mod26(x: i32) -> i32 {
    (x % 26 + 26) % 26 // 保证结果在 0 到 25 之间
}

fn create_key_matrix(linar: &Vec<i32>, n: usize) -> DMatrix<i32> {
    let len = linar.len();
    let mut result = DMatrix::zeros(n, n);
    for i in 0..n {
        for j in 0..n {
            let idx = i * n + j;
            result[(i, j)] = if idx < len { linar[idx] } else { 0 };
        }
    }
    result
}

fn create_input_matrix(chars: &Vec<char>, n: usize) -> DMatrix<i32> {
    let len = chars.len();
    let row = (len + n - 1) / n;
    let mut result = DMatrix::zeros(row, n);
    for i in 0..row {
        for j in 0..n {
            let idx = i * n + j;
            if idx >= len {
                break;
            }
            result[(i, j)] = utils::delta_char(chars[idx]) as i32;
        }
    }
    result
}

static INV26_MAP: LazyLock<HashMap<i32, i32>> = LazyLock::new(|| {
    let mut map = HashMap::new();
    map.insert(1, 1);
    map.insert(3, 9);
    map.insert(5, 21);
    map.insert(7, 15);
    map.insert(9, 3);
    map.insert(11, 19);
    map.insert(15, 7);
    map.insert(17, 23);
    map.insert(19, 11);
    map.insert(21, 5);
    map.insert(23, 17);
    map.insert(25, 25);
    map
});

fn adjoint_matrix(matrix: &DMatrix<i32>) -> DMatrix<i32> {
    let (m, n) = matrix.shape();
    assert_eq!(m, n);
    let mut cofactor = DMatrix::zeros(n, n);

    for i in 0..n {
        for j in 0..n {
            let submatrix = matrix.map(|x| x as f64).remove_row(i).remove_column(j);
            cofactor[(i, j)] =
                submatrix.determinant() as i32 * if (i + j) % 2 == 0 { 1 } else { -1 };
        }
    }
    cofactor.transpose()
}

fn matrix_inv26(matrix: &DMatrix<i32>) -> Result<DMatrix<i32>, &'static str> {
    let (m, n) = matrix.shape();
    assert_eq!(m, n);
    let det = matrix.map(|x| x as f64).determinant() as i32;
    let det = mod26(det);
    // if inv26_map does not contain det, return None
    if let Some(&inv_n) = INV26_MAP.get(&det) {
        let adj = adjoint_matrix(matrix);
        let result = adj.map(|x| mod26(x * inv_n));
        Ok(result)
    } else {
        Err("The key matrix is not invertible")
    }
}

fn multipy_matrix(left: &DMatrix<i32>, right: &DMatrix<i32>) -> DMatrix<i32> {
    let (m, n) = left.shape();
    let (_t, p) = right.shape();
    assert_eq!(n, _t);
    let mut result = DMatrix::zeros(m, p);
    for i in 0..m {
        for j in 0..p {
            for k in 0..n {
                result[(i, j)] += mod26(left[(i, k)] * right[(k, j)]);
                result[(i, j)] %= 26;
            }
        }
    }
    result
}

fn max(a: usize, b: usize) -> usize {
    if a > b {
        a
    } else {
        b
    }
}

fn gather_text(raw_text: &str, matrix: &DMatrix<i32>) -> String {
    let size = matrix.ncols();
    let mat_len = matrix.nrows() * matrix.ncols();
    let raw_len = raw_text.len();
    let alpha_len = raw_text.chars().filter(|c| c.is_alphabetic()).count();
    let strip_tail_cnt = {
        let mut cnt = 0;
        let mut i = mat_len - 1;
        while matrix[(i / size, i % size)] == 0 {
            cnt += 1;
            if i == 0 {
                break;
            }
            i -= 1;
        }
        cnt
    };
    // nonalpha_len = raw_len - alpha_len
    // result_min_alpha_len = mat_len - strip_tail_cnt
    // result_len = max(result_min_alpha_len + nonalpha_len, raw_len)
    let nonalpha_len = raw_len - alpha_len;
    let result_min_alpha_len = mat_len - strip_tail_cnt;
    let result_len = max(result_min_alpha_len + nonalpha_len, raw_len);
    let mut result = String::with_capacity(result_len);
    // append string
    let mut alpha_idx = 0;
    let mut raw_idx = 0;
    for c in raw_text.chars() {
        if c.is_alphabetic() {
            // alpha
            result.push(utils::char_from_delta(
                mod26(matrix[(alpha_idx / size, alpha_idx % size)]) as u8,
                c.is_uppercase(),
            ));
            alpha_idx += 1;
        } else {
            // non-alpha
            result.push(c);
        }
        raw_idx += 1;
    }
    while raw_idx < result_len {
        result.push(utils::char_from_delta(
            mod26(matrix[(alpha_idx / size, alpha_idx % size)]) as u8,
            false,
        ));
        alpha_idx += 1;
        raw_idx += 1;
    }
    result
}

fn end_space_len(s: &str) -> usize {
    let mut cnt = 0;
    for c in s.chars().rev() {
        if c.is_whitespace() {
            cnt += 1;
        } else {
            break;
        }
    }
    cnt
}

fn encrypt(plaintext: &str, key: &Vec<i32>, size: usize) -> String {
    let end_whitespace_len = end_space_len(plaintext);
    let end_whitespace = plaintext[plaintext.len() - end_whitespace_len..].to_string();
    let alphabetic_chars = plaintext.chars().filter(|c| c.is_alphabetic()).collect();
    let key_matrix = create_key_matrix(key, size);
    let input = create_input_matrix(&alphabetic_chars, size);
    let encrypted = multipy_matrix(&input, &key_matrix);
    gather_text(&plaintext.trim_end(), &encrypted).to_string() + &end_whitespace
}

fn decrypt(ciphertext: &str, key: &Vec<i32>, size: usize) -> Result<String, String> {
    let end_whitespace_len = end_space_len(ciphertext);
    let end_whitespace = ciphertext[ciphertext.len() - end_whitespace_len..].to_string();
    let alphabetic_chars = ciphertext.chars().filter(|c| c.is_alphabetic()).collect();
    let key_matrix = create_key_matrix(key, size);
    let input = create_input_matrix(&alphabetic_chars, size);
    let inv = matrix_inv26(&key_matrix)?;
    let decrypted = multipy_matrix(&input, &inv);
    Ok(gather_text(&ciphertext.trim_end(), &decrypted) + &end_whitespace)
}

pub fn assert_key(s: &str) -> Result<Vec<i32>, String> {
    // whole alphabetic
    if s.chars().all(|c| c.is_alphabetic()) {
        return Ok(s.chars().map(|c| utils::delta_char(c) as i32).collect());
    }
    // split by comma or space
    let mut result = Vec::new();
    let re = Regex::new(r",\s*|\s+").unwrap();
    let list: Vec<&str> = re.split(s).collect();
    if list.is_empty() {
        return Err("Empty key".to_string());
    }
    for num in list {
        match num.parse::<i32>() {
            Ok(n) => result.push(n),
            Err(_) => return Err(format!("Invalid key: {}", num)),
        }
    }
    Ok(result)
}

pub fn assert_size(s: &str) -> Result<usize, String> {
    match s.parse::<usize>() {
        Ok(n) => Ok(n),
        Err(_) => Err("Invalid size".to_string()),
    }
}

pub fn command_entry(m: &clap::ArgMatches) {
    assert!(m.contains_id("operation"));
    let is_enc = m.get_flag("enc");
    let cipherkey = m.get_one::<Vec<i32>>("key").unwrap();
    let size = m.get_one::<usize>("size").unwrap().clone();

    let buffer = utils::get_buffer(&m);

    if is_enc {
        let ciphertext = encrypt(&buffer, &cipherkey, size);
        print!("{}", ciphertext);
    } else {
        match decrypt(&buffer, &cipherkey, size) {
            Ok(plaintext) => print!("{}", plaintext),
            Err(e) => utils::error_handle::string(e),
        }
    }
}
