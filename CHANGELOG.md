# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-04-02

### Added
- ✨ Hybrid Actor-Critic Agent with Transformer encoder
- ✨ Dynamic Scenario Generator (500+ unique bug patterns)
- ✨ Gymnasium/OpenAI Gym integration (Hub-ready)
- ✨ PPO training algorithm implementation
- ✨ Comprehensive training notebook (01_training_quickstart.ipynb)
- ✨ Evaluation and analysis notebook (02_evaluation_analysis.ipynb)
- ✨ GitHub Actions CI/CD pipeline
- ✨ PyPI release automation
- ✨ Docker and Docker Compose support
- ✨ Complete architecture documentation
- ✨ Deployment guide for cloud environments

### Changed
- 🔄 Refactored environment for Gymnasium compatibility
- 🔄 Improved observation encoding with transformer backbone
- 🔄 Enhanced reward system with granular feedback

### Fixed
- 🐛 File I/O safety checks
- 🐛 Subprocess timeout handling
- 🐛 CUDA memory management

### Documentation
- 📚 Added ARCHITECTURE.md with system design
- 📚 Added DEPLOYMENT.md with deployment instructions
- 📚 Added CONTRIBUTING.md for contributors
- 📚 Updated README with advanced features

---

## [0.1.0] - 2026-03-15

### Added
- 🎉 Initial release of OpenEnv ASR
- 📦 Core sandbox environment with Docker isolation
- 🎮 Action space: read_file, write_file, run_pytest
- 👁️ Observation space: file tree, content, parse tree, terminal output
- 🏆 Reward logic: test-based rewards
- 🌳 Tree-sitter AST parsing
- 🤖 Base agent architecture
- 🛡️ File I/O sandboxing and whitelisting
- 📝 Comprehensive README and documentation
- 🧪 Unit tests for core components

### Features
- Automated code repair environment
- Pytest integration
- Tree-sitter code parsing
- Human-in-the-loop support (framework)

---

## Planned Features (Roadmap)

### v0.3.0 (May 2026)
- [ ] Multi-agent training support
- [ ] Curriculum learning for bug difficulty
- [ ] Transfer learning capabilities
- [ ] Agent zoo with pre-trained models
- [ ] Benchmark suite

### v0.4.0 (June 2026)
- [ ] Support for Java, C++
- [ ] Code coverage tracking
- [ ] Performance profiling integration
- [ ] Active learning interface
- [ ] Web dashboard

### v0.5.0+ (Future)
- [ ] Real-time collaborative debugging
- [ ] Integration with major IDEs
- [ ] Commercial API
- [ ] Advanced reasoning capabilities

---

## How to Report Issues

If you find a bug or have a suggestion, please:
1. Check [existing issues](https://github.com/23444555323/openenv-asr/issues)
2. Create a new issue with a clear description
3. Include steps to reproduce for bugs
4. Provide your environment details

---

## Support

- **Issues**: [GitHub Issues](https://github.com/23444555323/openenv-asr/issues)
- **Discussions**: [GitHub Discussions](https://github.com/23444555323/openenv-asr/discussions)
- **Documentation**: [DEPLOYMENT.md](DEPLOYMENT.md)

---

**Last Updated**: 2026-04-02