#include <stdint.h>
#include "xorcipher.h"

void cipher_pure(char *c_msg, char* key, char* buf, int msg_len, int key_len)
{
    for (unsigned i = 0; i < msg_len; i++){
        buf[i] = ((int) c_msg[i] ^ key[i%key_len]);
    }
} 

