# Implementation status

This page is deliberately conservative. A feature is not considered implemented because it appears in a roadmap or compiles as an isolated prototype.

| Area | Status | Evidence required to promote |
|---|---|---|
| Upstream Linux execution engine | Imported at CI build time from iSH-AOK | Successful device build and upstream regression suite |
| ARM64 iOS app | CI build target configured | Successful Xcode build and device installation |
| Unsigned IPA release | Workflow implemented | Successful Actions run and release asset |
| Darwin host bridge | Initial isolated C prototype | Linked into app, unit tests, device tests |
| Linux rootfs import | Upstream facilities are the starting point | Archive security tests and multi-root device tests |
| BSD utilities | Planned | Named tools compiled, licensed, and tested |
| FreeBSD/OpenBSD/NetBSD guest ABI | Not implemented | Separate ABI, loader, syscall suite, and real userland tests |
| Local Docker/Compose engine | Not implemented | OCI runtime and isolation conformance tests |
| Meta-OS/multi-root integration | Design stage | Root manager, package/root switching, rollback tests |

## Current prototype boundary

`integration/bsd/darwin_host.c` is a small host adapter using public POSIX/Darwin interfaces. It is not linked into iSH-AOK yet and does not execute BSD binaries. The CI workflow performs a compile-only check so that the API surface remains buildable against the iOS SDK.
