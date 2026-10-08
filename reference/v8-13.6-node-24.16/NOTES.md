# V8 13.6.233.17 reference files, as shipped in Node v24.16.0

Copied unmodified from `deps/v8` and `tools/v8_gypfiles` of the `v8.16.0` tag of nodejs/node, for the
claims made in the top-level README. They are not compiled by this project. License: BSD-3-Clause (`LICENSE`).

| File | What it shows |
|---|---|
| `v8-version.h` | the exact V8 version: 13.6.233.17 |
| `ieee754.cc`, `ieee754.h` (`src/base/`) | V8's port of fdlibm: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `atan2`, `exp`, `log`, ... and `legacy::pow`, the fdlibm `e_pow.c` port. Line 1 reads "adapted from fdlibm". The `V8_USE_LIBM_TRIG_FUNCTIONS` blocks show the optional glibc-derived `sin`/`cos` that Node does not enable. |
| `numbers/ieee754.cc`, `numbers/ieee754.h` | `v8::internal::math::pow`, the function behind `Math.pow` and `**`: ECMAScript special cases, `y == 2` to `x*x`, `y == 0.5` to `sqrt(x + 0)`, then `std::pow` of the platform CRT when `v8_flags.use_std_math_pow` is set, else `legacy::pow`. |
| `flag-definitions.h` | line 1029: `DEFINE_BOOL(use_std_math_pow, true, ...)`. |
| `common.gypi`, `features.gypi`, `v8.gyp` | Node's V8 build configuration; none of them defines `V8_USE_LIBM_TRIG_FUNCTIONS`, so Node's `Math.sin` and `Math.cos` are the fdlibm versions. |

Upstream permalinks: https://github.com/nodejs/node/tree/v24.16.0/deps/v8/src/base and
https://github.com/nodejs/node/tree/v24.16.0/deps/v8/src/numbers
