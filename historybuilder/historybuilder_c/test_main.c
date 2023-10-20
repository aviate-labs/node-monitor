#include <assert.h>
#include <inttypes.h>
#include <stdio.h>
#include <string.h>
#include "jenkins.h"


void test_jenkins_one_at_a_time_hash() {
    char* key = "The quick brown fox jumps over the lazy dog";
    uint32_t result = jenkins_one_at_a_time_hash(key, strlen(key));
    assert(result == 0x519e91f5);
    printf("Test Passed: Hash: %" PRIu32 "\n", result);
}


int main() {
    // Run Tests
    test_jenkins_one_at_a_time_hash();
    // Return
    return 0;
}