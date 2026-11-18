#!/usr/bin/env python3
"""Apply the Termi-iOS native-libc compatibility patch to a pinned iSH-AOK tree.

The patch is intentionally strict and idempotent: unexpected upstream drift
fails CI rather than silently producing a partially patched binary.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    file = ROOT / path
    text = file.read_text(encoding="utf-8")
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one patch anchor, found {count}: {old[:100]!r}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


# These functions only transform caller-owned memory. Unlike the three
# filesystem calls below, they cannot observe host files, users or devices.
replace_once(
    "tools/check-native-libc.py",
    '    "memcpy", "memmove", "memset", "memcmp", "memchr", "bcopy", "bzero", "bcmp",\n',
    '    "memcpy", "memmove", "memset", "memcmp", "memchr", "memccpy", "bcopy", "bzero", "bcmp",\n'
    '    "strlcat", "strlcpy",\n',
)

# Declarations are visible before the force-included redirection macros.
replace_once(
    "kernel/native_libc.h",
    "int nlibc_rename(const char *from, const char *to);\n",
    "int nlibc_rename(const char *from, const char *to);\n"
    "int nlibc_renameat(int olddirfd, const char *oldpath, int newdirfd, const char *newpath);\n",
)
replace_once(
    "kernel/native_libc.h",
    "ssize_t nlibc_pwrite(int fd, const void *buf, size_t n, off_t off);\n",
    "ssize_t nlibc_pwrite(int fd, const void *buf, size_t n, off_t off);\n"
    "ssize_t nlibc_preadv(int fd, const struct iovec *iov, int count, off_t off);\n"
    "ssize_t nlibc_pwritev(int fd, const struct iovec *iov, int count, off_t off);\n",
)

# The *at wrapper preserves guest dirfd semantics, including Darwin's distinct
# AT_FDCWD value, and resolves both paths through the guest VFS.
replace_once(
    "kernel/native_libc.c",
    "int nlibc_rename(const char *from, const char *to) {\n"
    "    NATIVE_FRAME;\n"
    "    NLIBC_PATH(guest_from, from);\n"
    "    NLIBC_PATH(guest_to, to);\n"
    "    return (int) nlibc_ret(native_syscall(NATIVE_SYS_renameat, AT_FDCWD_, guest_from,\n"
    "            AT_FDCWD_, guest_to));\n"
    "}\n",
    "int nlibc_rename(const char *from, const char *to) {\n"
    "    return nlibc_renameat(AT_FDCWD, from, AT_FDCWD, to);\n"
    "}\n"
    "\n"
    "int nlibc_renameat(int olddirfd, const char *oldpath, int newdirfd, const char *newpath) {\n"
    "    NATIVE_FRAME;\n"
    "    NLIBC_PATH(guest_oldpath, oldpath);\n"
    "    NLIBC_PATH(guest_newpath, newpath);\n"
    "    return (int) nlibc_ret(native_syscall(NATIVE_SYS_renameat, nlibc_at_fd(olddirfd),\n"
    "            guest_oldpath, nlibc_at_fd(newdirfd), guest_newpath));\n"
    "}\n",
)

# Marshal the iovec array and every buffer into guest scratch, then issue one
# guest preadv/pwritev syscall. This retains the kernel's single-operation
# semantics and never lets Darwin's host descriptors or paths leak through.
replace_once(
    "kernel/native_libc.c",
    "ssize_t nlibc_pwrite(int fd_no, const void *buf, size_t n, off_t off) {\n"
    "    NATIVE_FRAME;\n"
    "    if (buf == NULL && n > 0)\n"
    "        return nlibc_fail(_EFAULT);\n"
    "    guest_addr_t guest_buf = native_scratch_put(buf, n);\n"
    "    if (guest_buf == 0 && n > 0)\n"
    "        return nlibc_fail(_ENOMEM);\n"
    "    return (ssize_t) nlibc_ret(native_syscall(NATIVE_SYS_pwrite, fd_no,\n"
    "            guest_buf, n, off));\n"
    "}\n",
    "ssize_t nlibc_pwrite(int fd_no, const void *buf, size_t n, off_t off) {\n"
    "    NATIVE_FRAME;\n"
    "    if (buf == NULL && n > 0)\n"
    "        return nlibc_fail(_EFAULT);\n"
    "    guest_addr_t guest_buf = native_scratch_put(buf, n);\n"
    "    if (guest_buf == 0 && n > 0)\n"
    "        return nlibc_fail(_ENOMEM);\n"
    "    return (ssize_t) nlibc_ret(native_syscall(NATIVE_SYS_pwrite, fd_no,\n"
    "            guest_buf, n, off));\n"
    "}\n"
    "\n"
    "struct nlibc_guest_iovec { guest_addr_t base; size_t len; };\n"
    "\n"
    "static ssize_t nlibc_pv_common(int fd_no, const struct iovec *iov, int count,\n"
    "        off_t off, bool write) {\n"
    "    NATIVE_FRAME;\n"
    "    /* Linux UIO_MAXIOV: reject invalid counts before allocating scratch. */\n"
    "    if (count < 0 || count > 1024 || (count > 0 && iov == NULL))\n"
    "        return nlibc_fail(_EINVAL);\n"
    "    if (count == 0)\n"
    "        return 0;\n"
    "\n"
    "    struct nlibc_guest_iovec guest_iov[count];\n"
    "    size_t total = 0;\n"
    "    for (int i = 0; i < count; i++) {\n"
    "        if (iov[i].iov_len > (size_t) SSIZE_MAX - total)\n"
    "            return nlibc_fail(_EINVAL);\n"
    "        if (iov[i].iov_len > 0 && iov[i].iov_base == NULL)\n"
    "            return nlibc_fail(_EFAULT);\n"
    "        total += iov[i].iov_len;\n"
    "        guest_addr_t base = write\n"
    "            ? native_scratch_put(iov[i].iov_base, iov[i].iov_len)\n"
    "            : native_scratch_alloc(iov[i].iov_len);\n"
    "        if (base == 0 && iov[i].iov_len > 0)\n"
    "            return nlibc_fail(_ENOMEM);\n"
    "        guest_iov[i].base = base;\n"
    "        guest_iov[i].len = iov[i].iov_len;\n"
    "    }\n"
    "\n"
    "    guest_addr_t guest_iov_addr = native_scratch_put(guest_iov, sizeof(guest_iov));\n"
    "    if (guest_iov_addr == 0)\n"
    "        return nlibc_fail(_ENOMEM);\n"
    "    sqword_t res = native_syscall(write ? NATIVE_SYS_pwritev : NATIVE_SYS_preadv,\n"
    "            fd_no, guest_iov_addr, count, off);\n"
    "    if (res < 0)\n"
    "        return nlibc_fail((int) res);\n"
    "\n"
    "    if (!write) {\n"
    "        size_t remaining = (size_t) res;\n"
    "        for (int i = 0; i < count && remaining > 0; i++) {\n"
    "            size_t copied = iov[i].iov_len < remaining ? iov[i].iov_len : remaining;\n"
    "            if (copied > 0 && native_scratch_get(iov[i].iov_base,\n"
    "                    guest_iov[i].base, copied) < 0)\n"
    "                return nlibc_fail(_EFAULT);\n"
    "            remaining -= copied;\n"
    "        }\n"
    "    }\n"
    "    return (ssize_t) res;\n"
    "}\n"
    "\n"
    "ssize_t nlibc_preadv(int fd_no, const struct iovec *iov, int count, off_t off) {\n"
    "    return nlibc_pv_common(fd_no, iov, count, off, false);\n"
    "}\n"
    "\n"
    "ssize_t nlibc_pwritev(int fd_no, const struct iovec *iov, int count, off_t off) {\n"
    "    return nlibc_pv_common(fd_no, iov, count, off, true);\n"
    "}\n",
)

# Route the exact host symbols to the guest wrappers.
replace_once(
    "kernel/native_libc.h",
    "#define rename      nlibc_rename\n",
    "#define rename      nlibc_rename\n#define renameat    nlibc_renameat\n",
)
replace_once(
    "kernel/native_libc.h",
    "#define pwrite                   nlibc_pwrite\n",
    "#define pwrite                   nlibc_pwrite\n"
    "#define preadv                   nlibc_preadv\n"
    "#define pwritev                  nlibc_pwritev\n",
)

print("Termi-iOS native-libc patch applied (or already present).")
