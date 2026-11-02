# threefinger

> **Get 1.1.5 or newer** — earlier versions stopped swiping after the Mac slept. `threefinger --version` to check, `threefinger --reinstall` to update.

Swipe with three fingers on the Mac trackpad to change tabs.

Left/right posts `Cmd-Shift-[` / `Cmd-Shift-]`. Works in Safari, Chrome, Firefox, and most tabbed apps.

![threefinger demo](demo.gif)

Move the system gestures to four fingers and you get a full set:

| Fingers | Swipe | Does |
| --- | --- | --- |
| Three | ← / → | Previous / next tab |
| Four | ↑ | Mission Control |
| Four | ↓ | App Exposé |
| Four | ← / → | Full-screen apps |

## Setup

1. Install and allow threefinger when Settings asks (**Accessibility** — on newer macOS **Device Control and Data Access** — and **Input Monitoring**; for threefinger, not Terminal):

   ```sh
   curl -fsSL https://raw.githubusercontent.com/firedev/threefinger/master/install.sh | bash
   threefinger --check --open
   ```

   Or: `brew install firedev/tap/threefinger && brew services start threefinger`

2. In **Trackpad → More Gestures**, move everything to four fingers so macOS doesn’t steal the three-finger swipe:
   - **Mission Control** → **Swipe Up with Four Fingers**
   - **App Exposé** → **Swipe Down with Four Fingers**
   - **Swipe between full-screen applications** → **Swipe Left or Right with Four Fingers**
   - **Swipe between pages** → **Off** (optional)

Then swipe.

More: [firedev.com/projects/threefinger](https://firedev.com/projects/threefinger/)

## Update / repair

```sh
threefinger --reinstall
```

Stops every copy (curl or Homebrew), installs the latest release, re-checks permissions. Re-running the curl one-liner from Setup does the same thing — both are safe to run over an existing install.

Switching from Homebrew to the curl install (one daemon, no rebuild on upgrade):

```sh
brew uninstall threefinger
curl -fsSL https://raw.githubusercontent.com/firedev/threefinger/master/install.sh | bash
```

## Config

Edit `~/.config/threefinger.json` (Karabiner-style). By default, left/right change tabs; you can map any shortcut. Restart after editing:

```sh
brew services restart threefinger
# or, if you used the curl installer:
launchctl kickstart -k gui/$UID/com.firedev.threefinger
```

### Send a URL action to a running app

A `to` action can instead specify a `url` and the target app's `bundle_id`.
threefinger sends the URL directly as a `get URL` Apple event, without opening
the app through Launch Services. The app must already be running and must
support that URL action. macOS may ask for permission to control the app under
**Privacy & Security → Automation**. A failed or denied action is logged.

For example, with HyprMac's **Allow other apps to control HyprMac** enabled:

```json
{
  "description": "Cycle HyprMac workspaces",
  "manipulators": [
    { "from": { "gesture": "three_finger_swipe_left" }, "to": [
      { "bundle_id": "com.zachgray.HyprMac", "url": "hyprmac://action/cycleWorkspace?delta=1" }
    ] },
    { "from": { "gesture": "three_finger_swipe_right" }, "to": [
      { "bundle_id": "com.zachgray.HyprMac", "url": "hyprmac://action/cycleWorkspace?delta=-1" }
    ] }
  ]
}
```

Each action must specify either `key_code` (with optional `modifiers`) or
both `url` and `bundle_id`. URL actions do not launch a stopped app.
While a URL action sequence is running, further URL gestures are dropped
rather than queued. Keyboard-only gestures remain responsive. Actions within
a sequence run in order; a failed action is logged and the sequence continues.

## Development checks

Run `python3 tests/check.py` to check configuration validation and gesture
scheduling without posting keyboard events or controlling applications.

## Build from source

```sh
git clone https://github.com/firedev/threefinger && cd threefinger
make install
```

## Uninstall

```sh
# curl install
curl -fsSL https://raw.githubusercontent.com/firedev/threefinger/master/uninstall.sh | bash

# Homebrew
brew uninstall threefinger

# from a clone
make uninstall
```

> Use **either** Homebrew **or** the curl installer — not both. Two daemons will fight over the same swipe.

> From 1.2.0 the release binary is signed, so upgrades keep the Accessibility grant. Coming from 1.1.x or a Homebrew build (ad-hoc signed, every upgrade), the old entry stops working even though it still shows as on. Select threefinger, click **−**, then **+** → `~/.local/bin/threefinger`. The daemon restarts itself once granted.

## License

MIT. Tiny Swift tool on MultitouchSupport — a one-feature BetterTouchTool replacement.
