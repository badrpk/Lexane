# HuobzLang — High-Level Compact Language for AI

**A compact semantic language and intermediate representation designed to express more meaning with fewer tokens and lower compute overhead.**

HuobzLang is the canonical language component of the **Shmry Software Inc** ecosystem. It provides compact language, semantic encoding, tokenization, and low-compute representation services for Sophyane, Neuron, Xerus, Nifdu, Shmry, and VPS integrations.

## Why HuobzLang

HuobzLang is intended to make AI and software systems communicate with a smaller, denser representation layer instead of repeatedly expanding work into verbose natural-language or implementation-specific forms.

Core directions include:

- compact semantic representation
- high-level language / IR
- tokenizer support
- semantic encoding
- low-compute model interfaces
- efficient exchange between ecosystem components

## Shmry Software Inc ecosystem

| Product | Role |
|---|---|
| Shmry | Cloud + email server |
| Xerus | Disk-first memory |
| VPS | Native TLS/SNI webserver |
| **HuobzLang** | **Highest-level compact language** |
| Neuron | Biological intelligence |
| Nifdu | Screenshot-loop harness |
| Sophyane | Multi-option engineering harness |

When a required capability is unavailable locally, HuobzLang can request the appropriate peer capability according to the shared ecosystem contract.

## Current source status

HuobzLang was previously redirected into the broader `badrpk/huobz` monorepo. This repository is now restored as the canonical public identity for the language itself.

The fuller historical Huobz workspace still contains additional AI-coder and monorepo material. Only language-specific source, tokenizer, semantic-encoding, model/training helpers, documentation, and tests should be promoted here as the canonical HuobzLang implementation.

## Download

```bash
git clone https://github.com/badrpk/HuobzLang.git
cd HuobzLang
```

A universal installer will be added after the canonical local HuobzLang implementation is promoted and its platform requirements are verified.

## Ecosystem contract

See [`ecosystem.json`](ecosystem.json).

## Contributing

Contributions are welcome in compact language design, tokenizer efficiency, semantic IR design, low-compute representation, tests, and interoperability with the other Shmry Software Inc products.

## Security

Do not commit API keys, model-provider credentials, private keys, `.env` files, local model caches, or machine-specific secrets.

## License

See repository license files for the applicable terms.
