# Individual Flags CTFd Plugin

A CTFd plugin to make challenges that have per-user flags. This will introduce a new challenge type where flags
can be configured per user to contain bytes derived with a keyed hash function to make it different (or at least
likely different) from other users.

# How to install plugin

TODO

# How to use plugin

1. Create a new challenge with the type `individual` with a static flag with the format listed below.
2. Add a flag with the type `key` to add an HMAC-SHA-256 key that'll be used to make the flag unique per person. See below for how to get what the per-user data will be.


# Documentation

## `static` flag format that should be used with `individual` challenges

When making `individual` challenges, there should be a static flag containing a special string that will
be replaced with the random bytes from the keyed hash function. The special string is of the following format
`%%%%<number of hex digits; 1-64>%%%%`. For example, `%%%%16%%%%` would be replaced with 16 hex digits (8 bytes) from the
keyed hash generated as described in the section below. If something other than 1-64 is provided for the number of hex digits,
an error will be generated upon flag submission.

Static flag example: `my_ctf{flag_text_before_%%%%16%%%%_more_text_after}`.

Note: Only the first occurrence of the string above is replaced.

## `key` flag type

When adding this flag type, a securely generated string of 32 random bytes in hex is pre-populated into the field to be used as
the HMAC-SHA-256 key to generate the per-user part of the flag. A custom key may also be provided.

## What the per-user part contains

The per-user part of the flag will be replaced with the specified number of bytes from an HMAC SHA-256 digest.
The key used for this will be the one specified in the way above. The input to the HMAC will be the email of the
user submitting the flag.

# Future work

1. Add a way to individualize file distribution
2. Add separate templates to use for challenges, not just from standard
3. Test/enable compatibility with teams mode.
