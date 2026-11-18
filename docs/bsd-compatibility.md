# BSD and Darwin compatibility

## Three different targets

### 1. BSD/POSIX tools compiled for Darwin

This is the most practical first step. Selected utilities can be compiled as part of the iOS app and exposed through a controlled native-command registry. They execute as host ARM64 code and must be carefully shimmed so that environment, identity, paths, current directory, and file access reflect the selected guest root rather than leaking host application state.

### 2. BSD userlands running on the Linux compatibility engine

A FreeBSD/OpenBSD/NetBSD rootfs archive is not automatically executable. Their ELF binaries use OS-specific ABI conventions and syscall tables. A real guest implementation needs, at minimum:
- ELF machine and OS ABI validation.
- A distinct guest ABI identifier per supported BSD.
- BSD syscall dispatch and argument marshalling.
- BSD errno, signal, process, thread, and wait semantics.
- BSD-specific `mmap`, `ioctl`, `fcntl`, `kqueue`, `sysctl`, and socket behavior.
- Required virtual filesystems and device semantics.
- Dynamic loader and libc compatibility.
- Regression tests built from the target BSD userland.

The Linux syscall table must not be reused by simply renumbering syscall IDs.

### 3. Darwin host services

iOS is built on Darwin/XNU and exposes a BSD-derived userspace API. Termi-iOS may use public APIs that are available to ordinary sandboxed applications, such as POSIX file descriptors, sockets, `kqueue` where supported, `posix_spawn`, `sysctl` for permitted queries, and standard libc facilities.

This does not grant kernel privileges. Private APIs, kernel extensions, arbitrary mounts, unrestricted device access, and loading third-party kernel modules are out of scope.

## Initial implementation policy

- Prefer public Apple SDK APIs and portable POSIX interfaces.
- Keep host operations behind a narrow adapter.
- Never treat host PID, UID, filesystem paths, or network state as guest values without explicit translation.
- Use capability checks and return a clear unsupported error for unavailable operations.
- Keep BSD guest ABI work isolated from Linux ABI code.
- Add tests for every claimed compatibility behavior.

## Compatibility labels

Use precise labels in the app:
- **Native Darwin tool:** compiled for iOS and running as host code.
- **Linux guest program:** executed through the Linux compatibility engine.
- **BSD-compatible tool:** a selected program tested against its stated BSD/POSIX behavior.
- **BSD guest binary:** only use this label after that BSD's executable ABI and syscall suite pass.
