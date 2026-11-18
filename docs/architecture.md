# Termi-iOS architecture

## Runtime layers

1. **iOS application (ARM64):** Swift/Objective-C UI and platform integration, built for iPhoneOS.
2. **Darwin host bridge:** public libc, file coordination, sandbox storage, sockets, timers, terminal I/O, and other supported iOS APIs.
3. **Linux compatibility engine:** iSH-AOK guest CPU/JIT, Linux syscall translation, process/task model, signals, virtual memory, and filesystem abstractions.
4. **Root filesystem manager:** validated tar archive import, extraction into app-managed storage, root metadata, and safe activation/rollback.
5. **Userland:** Alpine first; additional Linux roots only when their ABI and package assumptions are supported.
6. **Optional compatibility layers:** selected BSD/POSIX host tools and, later, a separately designed BSD guest ABI.

## ARM64 terminology

The app itself is compiled as ARM64 machine code. A guest ARM64 Linux process is still handled by the guest execution engine unless a particular operation is explicitly implemented as a safe native host fast path. Same-ISA does not by itself mean that arbitrary Linux binaries can execute directly on Darwin.

## Root archive import

The importer must:
- Accept only recognized tar formats (including gzip and xz compression).
- Reject absolute paths, parent-directory traversal, unsafe links, device nodes, and entries escaping the destination.
- Enforce extraction size, file-count, and path-length limits.
- Preserve Unix ownership/mode metadata only where meaningful and permitted.
- Extract into a staging directory, validate essential rootfs files, then atomically activate it.
- Never overwrite the active rootfs in place.

## Container roadmap

A container feature is not complete merely because `docker` or `docker compose` commands exist. The roadmap is:
- OCI image manifest/layer parsing.
- Layered filesystem and copy-on-write semantics.
- Process lifecycle and namespaces.
- Resource accounting/isolation equivalent to the required cgroup features, or an explicit documented compatibility subset.
- Network isolation and port forwarding.
- OCI runtime integration and conformance tests.

Until these are implemented, the UI must label local container support experimental or unavailable. Remote Docker contexts can be considered as a separate feature.

## Milestones

- **M0 — Build foundation:** reproducible upstream checkout, unsigned ARM64 IPA, release automation.
- **M1 — Product identity:** Termi-iOS bundle identity, app display name, rootfs catalogue and import UX.
- **M2 — Linux fidelity:** syscall coverage, procfs/sysfs behavior, signals, process semantics, filesystem conformance.
- **M3 — BSD/POSIX bridge:** selected native utilities and Darwin-backed POSIX services.
- **M4 — BSD guest ABI research:** FreeBSD first as a separate ABI with executable and syscall test suites.
- **M5 — OCI research:** storage, runtime, networking, and isolation feasibility.
- **M6 — Meta-OS:** multiple installed roots, shared host-managed catalogue, safe root switching, and documented cross-root execution.

Every milestone needs tests on a real device. Simulator-only success is insufficient for performance, memory, lifecycle, and sandbox behavior.
