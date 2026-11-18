# Termi-iOS

**Termi-iOS** is an experimental Unix/Linux compatibility environment for iOS, built on the open-source [iSH-AOK](https://github.com/emkey1/ish-AOK) project.

This repository owns the Termi-iOS product configuration, integration layer, documentation, tests, and release automation. The upstream iSH-AOK source is checked out at build time by GitHub Actions, so upstream source and submodule licenses/attributions remain intact.

## Project goals

- ARM64 iOS application, compiled for `iphoneos`.
- Linux userspace through iSH-AOK's syscall-translation and JIT architecture.
- Alpine Linux minirootfs as the initial distribution.
- Import additional root filesystems from supported `.tar.gz`, `.tar.xz`, and other tar archives, subject to archive validation and filesystem compatibility.
- A compatibility layer for selected BSD/POSIX userland programs.
- Darwin/iOS host bridges using public APIs available to sandboxed apps.
- Long-term exploration of BSD ABI support, OCI containers, and multi-root/meta-distribution workflows.

## Important platform boundaries

Termi-iOS is **not** a Linux or BSD kernel running on the iPhone. Third-party iOS apps cannot replace the Darwin kernel, load arbitrary kernel modules, or use hardware virtualization as a general-purpose VM facility. Linux support therefore relies on user-mode emulation and syscall translation.

Likewise, Docker CLI and Compose alone do not provide a Docker Engine. A local OCI/container implementation would require compatible process isolation, namespaces, cgroups/resource controls, networking, mounts, and storage semantics. These are research targets; they must not be advertised as working until implemented and tested.

## BSD strategy

The first milestone is a Darwin-host compatibility bridge and a curated BSD/POSIX utility layer. Running unmodified FreeBSD, OpenBSD, or NetBSD ELF binaries requires a separate BSD ABI implementation: executable loading, syscall numbering/semantics, signals, process model, virtual filesystems, and per-OS userland assumptions. This is a distinct milestone, not something achieved by importing a BSD rootfs tarball.

See [docs/architecture.md](docs/architecture.md) and [docs/bsd-compatibility.md](docs/bsd-compatibility.md).

## Build and release

GitHub Actions checks out the upstream `emkey1/ish-AOK` source and its submodules, applies the Termi-iOS build identity, compiles the iOS ARM64 app without Apple code signing, packages an IPA, and publishes it as a GitHub Release.

- Workflow: [Build unsigned IPA](.github/workflows/release-ipa.yml)
- Releases: [GitHub Releases](https://github.com/vjnzbcsbgf-maker/Termi-iOS/releases)

The first build is an upstream-derived baseline. It is not yet a completed implementation of the additional BSD, Docker, or Meta-OS goals.

## Licensing and attribution

iSH-AOK is a separate upstream project. Its source, submodules, assets, and resulting binary retain their respective licenses and notices. Termi-iOS-specific files in this repository are licensed under GPL-2.0-or-later unless a file says otherwise. Review all upstream and dependency notices before redistributing builds.
