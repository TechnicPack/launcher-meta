# Technic Launcher Meta

A Python-based tool for fetching, processing, and maintaining Minecraft version metadata for the Technic Launcher. This repository contains optimized Minecraft version manifests with reduced file sizes and filtered content specifically tailored for the Technic platform.

## Overview

This project automatically downloads Minecraft version manifests from Mojang's launcher meta API, processes them to remove unnecessary components, and stores them in a structured format. The processed manifests are optimized for use with the Technic Launcher by:

- Removing unused downloads (server, mappings)
- Filtering out unnecessary library classifiers (javadoc, sources)
- Stripping logging configurations and compliance levels
- Validating game arguments and feature flags
- Optimizing native library handling

## Features

- **Automated Version Updates**: Fetches the latest Minecraft versions from Mojang's API
- **Smart Processing**: Removes bloat while preserving essential launcher functionality
- **Validation**: Ensures all game arguments use known variables and features
- **Native Optimization**: Handles architecture-specific native libraries efficiently
- **Change Detection**: Only updates files when actual changes are detected

## Repository Structure

```
launcher-meta/
├── version/                    # Processed Minecraft version manifests
│   ├── 1.21.8/
│   │   └── 1.21.8.json        # Optimized version manifest
│   ├── 1.21.7/
│   ├── 1.20.6/
│   └── ...                    # All supported MC versions
├── update_versions.py         # Main processing script
├── pyproject.toml            # Poetry dependencies
├── renovate.json             # Dependency update configuration
└── README.md                 # This file
```

## Requirements

- Python 3.12+
- aiohttp (with speedups)
- packaging

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd launcher-meta
```

2. Install dependencies using Poetry:
```bash
poetry install
```

Or with pip:
```bash
pip install aiohttp[speedups] packaging
```

## Usage

### Update Version Manifests

Run the main script to fetch and process the latest Minecraft versions:

```bash
python update_versions.py
```

The script will:
1. Fetch the version manifest from Mojang's API
2. Process each release version (skipping snapshots)
3. Generate optimized manifests in the `version/` directory
4. Report new and updated versions

### Processing Details

The script performs several optimizations:

- **Download Filtering**: Keeps only client downloads, removes server and mappings
- **Library Optimization**: Filters native libraries based on supported architectures
- **Argument Validation**: Validates game arguments against known variables and features
- **Java Version Defaults**: Ensures compatibility with older versions
- **Size Optimization**: Removes unnecessary metadata and configurations

## Supported Features

The following Minecraft launcher features are supported:

- `is_demo_user`
- `has_custom_resolution`
- `has_quick_plays_support`
- `is_quick_play_singleplayer`
- `is_quick_play_multiplayer`
- `is_quick_play_realms`

## Supported Variables

All standard Minecraft launcher variables are supported, including:

- Authentication: `auth_username`, `auth_session`, `auth_access_token`, etc.
- Game settings: `game_directory`, `resolution_width`, `resolution_height`
- Assets: `assets_root`, `assets_index_name`
- System: `natives_directory`, `classpath`

## Configuration

### Renovate Bot

This repository uses Renovate Bot for automated dependency updates. Configuration is in `renovate.json`:

- Automatically merges compatible updates
- Separates major version releases
- Assigns updates to maintainer @Pyker

### Architecture Support

The tool supports the following native architectures:
- 32-bit (`32`)
- 64-bit (`64`)

## Development

### Code Structure

- `process_version()`: Main processing function for individual version manifests
- `KNOWN_FEATURES`: Whitelist of supported launcher features
- `KNOWN_VARIABLES`: Whitelist of supported template variables
- `SUBSTITUTION_REGEX`: Pattern for finding template variables in arguments

### Error Handling

The script includes comprehensive validation:
- Unknown features trigger immediate termination
- Unknown variables are flagged as errors
- Missing native libraries generate warnings for older versions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure all validation passes
5. Submit a pull request

## License

This project is maintained by the Technic team (@Pyker). Please refer to the project's license file for usage terms.

## Acknowledgments

- Mojang Studios for providing the launcher meta API
- The Technic community for feedback and testing

---

*This tool is designed specifically for the Technic Launcher and may not be suitable for other Minecraft launchers without modification.*
