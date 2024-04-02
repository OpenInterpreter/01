<h1 align="center">○</h1>

<p align="center">
    <a href="https://discord.gg/Hvz9Axh84z"><img alt="Discord" src="https://img.shields.io/discord/1146610656779440188?logo=discord&style=social&logoColor=black"/></a>
    <br>
    <br>
    <strong>Le modèle de langage d'ordinateur open-source.</strong><br>
    <br><a href="https://openinterpreter.com/01">Précommandez le Light</a>‎ ‎ |‎ ‎ <a href="https://changes.openinterpreter.com">Recevoir les mises à jour</a>‎ ‎ |‎ ‎ <a href="https://01.openinterpreter.com/">Documentation</a><br>
</p>

<br>

![OI-O1-BannerDemo-2](https://www.openinterpreter.com/OI-O1-BannerDemo-3.jpg)

Nous voulons vous aider à construire. [Postulez pour un support individuel.](https://0ggfznkwh4j.typeform.com/to/kkStE8WF)

<br>

---

⚠️ **ATTENTION** : Ce projet expérimental est en développement rapide et manque de protections de sécurité de base. Jusqu'à l'atteinte d'une version stable 1.0, veuillez faire fonctionner ce dépôt **uniquement** sur des appareils ne contenant aucune information sensible et n'ayant pas accès à des services payants.

---

<br>

**Le Projet 01** construit un écosystème open source pour les appareils d'IA.

Notre système d'exploitation phare peut alimenter des dispositifs conversationnels tels que le Rabbit R1, le Humane Pin, ou [l'ordinateur de Star Trek](https://www.youtube.com/watch?v=1ZXugicgn6U).

Nous avons l'intention de devenir le GNU/Linux de cet environnement en restant ouvert, modulaire et gratuit.

<br>

# Software

```shell
git clone https://github.com/OpenInterpreter/01 # Clone le dépôt
cd 01/software # CD dans le répertoire source
```

<!-- > Cela ne fonctionne pas ? Lisez notre [guide d'installation](https://docs.openinterpreter.com/getting-started/setup). -->

```shell
brew install portaudio ffmpeg cmake # Installe les dépendances Mac OSX
poetry install # Installe les dépendances Python
export OPENAI_API_KEY=sk... # OU exécute `poetry run 01 --local` pour tout exécuter localement
poetry run 01 # Exécute le simulateur 01 Light (maintenez votre barre d'espace, parlez, relâchez)
```

<!-- > Pour une installation sous Windows, lisez [le guide dédié](https://docs.openinterpreter.com/getting-started/setup#windows). -->

<br>

# Hardware

- Le **01 Light** est une interface vocale basée sur ESP32. Les instructions de construction sont [ici]. (https://github.com/OpenInterpreter/01/tree/main/hardware/light). Une liste de ce qu'il faut acheter se trouve [ici](https://github.com/OpenInterpreter/01/blob/main/hardware/light/BOM.md).
- Il fonctionne en tandem avec le **Server 01** ([guide d'installation ci-dessous](https://github.com/OpenInterpreter/01/blob/main/README.md#01-server)) fonctionnant sur votre ordinateur.
- **Mac OSX** et **Ubuntu** sont pris en charge en exécutant `poetry run 01` (**Windows** est pris en charge de manière expérimentale). Cela utilise votre barre d'espace pour simuler le 01 Light.
- (prochainement) Le **01 Heavy** est un dispositif autonome qui exécute tout localement.

**Nous avons besoin de votre aide pour soutenir et construire plus de hardware.** Le 01 devrait pouvoir fonctionner sur tout dispositif avec entrée (microphone, clavier, etc.), sortie (haut-parleurs, écrans, moteurs, etc.) et connexion internet (ou suffisamment de puissance de calcul pour tout exécuter localement). [Guide de Contribution →](https://github.com/OpenInterpreter/01/blob/main/CONTRIBUTING.md)

<br>

# Comment ça marche ?

Le 01 expose un websocket de *speech-to-speech* à l'adresse `localhost:10001`.

Si vous diffusez des octets audio bruts vers `/` au [format de streaming LMC](https://docs.openinterpreter.com/guides/streaming-response), vous recevrez sa réponse dans le même format.

Inspiré en partie par [l'idée d'un OS LLM d'Andrej Karpathy](https://twitter.com/karpathy/status/1723140519554105733), nous utilisons un [un modèle de langage inteprétant du code](https://github.com/OpenInterpreter/open-interpreter), et le sollicitons lorsque certains événements se produisent dans le [noyau de votre ordinateur](https://github.com/OpenInterpreter/01/blob/main/software/source/server/utils/kernel.py).

Le 01 l'encapsule dans une interface vocale :

<br>

<img width="100%" alt="LMC" src="https://github.com/OpenInterpreter/01/assets/63927363/52417006-a2ca-4379-b309-ffee3509f5d4"><br><br>

# Protocoles

## Messages LMC

Pour communiquer avec les différents composants du système, nous introduisons le [format de messages LMC](https://docs.openinterpreter.com/protocols/lmc-messages), une extension du format de message d'OpenAI qui inclut un nouveau rôle "*computer*":

https://github.com/OpenInterpreter/01/assets/63927363/8621b075-e052-46ba-8d2e-d64b9f2a5da9

## Messages Systèmes Dynamiques (Dynamic System Messages)

Les Messages Systèmes Dynamiques vous permettent d'exécuter du code à l'intérieur du message système du LLM, juste avant qu'il n'apparaisse à l'IA.

```python
# Modifiez les paramètres suivants dans i.py
interpreter.system_message = r" The time is {{time.time()}}. " # Tout ce qui est entre doubles crochets sera exécuté comme du Python
interpreter.chat("What time is it?") # L'interpréteur connaitre la réponse, sans faire appel à un outil ou une API
```

# Guides

## 01 Server

Pour exécuter le serveur sur votre ordinateur et le connecter à votre 01 Light, exécutez les commandes suivantes :

```shell
brew install ngrok/ngrok/ngrok
ngrok authtoken ... # Utilisez votre authtoken ngrok
poetry run 01 --server --expose
```

La dernière commande affichera une URL de serveur. Vous pouvez saisir ceci dans le portail WiFi captif de votre 01 Light pour le connecter à votre serveur 01.

## Mode Local

```
poetry run 01 --local
```

Si vous souhaitez exécuter localement du speech-to-text en utilisant Whisper, vous devez installer Rust. Suivez les instructions données [ici](https://www.rust-lang.org/tools/install).

## Personnalisation

Pour personnaliser le comportement du système, modifie [`system message`, `model`, `skills library path`,](https://docs.openinterpreter.com/settings/all-settings) etc. in `i.py`. Ce fichier configure un interprète alimenté par Open Interpreter.

## Dépendances Ubuntu

```bash
sudo apt-get install portaudio19-dev ffmpeg cmake
```

# Contributeurs

[![01 project contributors](https://contrib.rocks/image?repo=OpenInterpreter/01&max=2000)](https://github.com/OpenInterpreter/01/graphs/contributors)

Veuillez consulter nos [directives de contribution](CONTRIBUTING.md) pour plus de détails sur comment participer.

<br>

# Roadmap

Visitez [notre roadmap](/ROADMAP.md) pour connaitre le futur du 01.

<br>

## Background

### [Contexte ↗](https://github.com/KillianLucas/01/blob/main/CONTEXT.md)

L'histoire des appareils qui ont précédé le 01.

### [Inspiration ↗](https://github.com/KillianLucas/01/tree/main/INSPIRATION.md)

Des choses dont nous souhaitons nous inspirer.

<br>

○
