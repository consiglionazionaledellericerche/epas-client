# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2020-11-18
### Added
- Possibilità di monitoraggio dei job del client tramite un meccanismo di invio
 delle metriche ad un PushGateway Prometheus 
- File VERSION per il semantic version dell'applicazione
- File CHANGELOG.md

### Changed
- Rimossa classe stampingSender.StampingSender effettuando il _push up_ del 
metodo _send_ che ne era contenuto e che è stato rinominato in _sendStamping_
- Rimossa classe client.StampingClient ed effettuato _push up_ del metodo
process\_stamping\_files

## [1.0.0] - 2020-11-10
### Added
- First public open source release