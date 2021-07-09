//XORCIPHER.RS
use std::slice;

#[no_mangle]
pub fn cipher(msg: *const i8, key: *const i8, buf: *mut i8, msg_len: usize, key_len: usize)
{
    let msg = unsafe { slice::from_raw_parts(msg, msg_len) };
    let key = unsafe { slice::from_raw_parts(key, key_len) };
    for i in 0..msg_len{
        unsafe{let new_p = buf.offset(i as isize);
        let val = msg[i] ^ key[i % key_len];
        *new_p = val;
        }
    }
    return;
}

