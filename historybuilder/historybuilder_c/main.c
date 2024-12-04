#include <stdio.h>
#include <inttypes.h>
#include <string.h>
#include "jenkins.h"

int main() {
   // Run Jenkins Hash
   char* key = "Hello, World!";
   uint32_t result = jenkins_one_at_a_time_hash(key, strlen(key));
   printf("Hash: %" PRIu32 "\n", result);
}
