Run the metadata selection and PFS0 tests with Python's standard library:

```sh
python3 -m unittest discover -s tests -v
```

To also run the encrypted package tests, install the project's Python dependencies
and set `NSCB_NCA_TESTS=1`:

```sh
NSCB_NCA_TESTS=1 python3 -m unittest discover -s tests -v
```

These tests use the real `Fs.Nca` reader and writer with invented AES keys and
synthetic CNMT/PFS0 content. They disable unrelated database initialization and
the unused extraction backend. No console keys, game dumps, network access, or
emulator are needed. The package tests verify Control reference selection, the
`1.0.0` to `1.4.2` display-version lookup, preserved payloads, regenerated XML,
all three NCA hash layers, and atomic failure recovery. They do not verify game
execution or Astris UI behavior.
