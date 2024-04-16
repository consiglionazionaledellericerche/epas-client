# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2024-04-17
### Added
- Introdotto meccanismo per attribuzione causale pausa pranzo durante la rispettiva fascia oraria 

## [1.3.0] - 2023-03-14
### Added
- Corretto esempio Regex di Default
- Introdotta CI per la build dell'immagine docker

## [1.2.3] - 2021-03-08
### Changed
- Ritorno alla python:3-alpine con builder separato per diminuire dimensioni immagine,
grazie a @callido-serpe e @GothoRemotho per la modifica.
- Fix __str__ di Stamping per i casi in cui alcuni attributi non sono presenti 

## [1.2.2] - 2021-01-15
### Changed
- Fix configurazione cron per compatibilità con Debian (immagine docker python:3-slim) 

## [1.2.1] - 2021-01-14
### Added
- Aggiunto package cron non presente nella python:3-slim. 

## [1.2.0] - 2021-01-14
### Changed
- Modificata immagine docker di base da python:3-alpine a python:3-slim per
ridurre i tempi di build e la dimensione dell'immagine. 

## [1.1.1] - 2021-01-07
### Added
- Aggiunto parametro CHECK_SUCCESS_MSG per compatibilità con vecchi lettori
smartclock, grazie a @angelo.salvarani per la modifica.

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
- Corretta apertura in scrittura del file da scaricare via FTP.

## [1.0.0] - 2020-11-10
### Added
- First public open source release