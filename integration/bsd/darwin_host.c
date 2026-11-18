#include "darwin_host.h"

#include <errno.h>
#include <stdlib.h>
#include <time.h>
#include <sys/event.h>
#include <unistd.h>

int termios_host_uname(struct utsname *result) {
    if (result == NULL) {
        return EINVAL;
    }
    if (uname(result) != 0) {
        return errno;
    }
    return 0;
}

int termios_host_monotonic_ns(uint64_t *result) {
    if (result == NULL) {
        return EINVAL;
    }

    struct timespec now;
    if (clock_gettime(CLOCK_MONOTONIC, &now) != 0) {
        return errno;
    }

    *result = ((uint64_t)now.tv_sec * UINT64_C(1000000000))
            + (uint64_t)now.tv_nsec;
    return 0;
}

int termios_host_random(void *buffer, size_t length) {
    if (buffer == NULL && length != 0) {
        return EINVAL;
    }
    if (length != 0) {
        arc4random_buf(buffer, length);
    }
    return 0;
}

int termios_host_kqueue_create(void) {
    int fd = kqueue();
    return fd < 0 ? -errno : fd;
}
