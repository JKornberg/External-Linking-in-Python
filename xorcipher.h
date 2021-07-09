#pragma once
#include <cstdint>
#include <stdint.h>

extern "C"
{
  void cipher_pure(char *c_msg, char* key, char* buf, int msg_len, int key_len);
}

