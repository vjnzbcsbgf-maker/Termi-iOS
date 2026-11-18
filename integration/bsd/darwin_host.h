#ifndef TERMIOS_DARWIN_HOST_H
#define TERMIOS_DARWIN_HOST_H

/*
 * Minimal, public-API-only Darwin host bridge.
 *
 * These functions describe the iOS host, not a Linux/BSD guest. Callers must
 * explicitly translate or virtualize returned values before exposing them to
 * guest processes.
 */

#include <stddef.h>
#include <stdint.h>
#include <sys/utsname.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Return 0 on success, otherwise an errno value. */
int termios_host_uname(struct utsname *result);
int termios_host_monotonic_ns(uint64_t *result);
int termios_host_random(void *buffer, size_t length);

/* Returns a kqueue descriptor, or a negative errno value. Caller owns fd. */
int termios_host_kqueue_create(void);

#ifdef __cplusplus
}
#endif

#endif /* TERMIOS_DARWIN_HOST_H */
