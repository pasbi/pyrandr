# pyrandr
Yet another Python wrapper around xrandr.

## Motivation
This one is specific to my use case.
I used to use `arandr` to configure the screens and generate a small shell script (basically a call to xrandr with a lot of arguments).
The problem is:

- The name of the screens don't seem to be stable. Today my large screen is connected to DP-3-2, tomorrow it might be DP-1-2. I don't know why, maybe because I use different docking stations. Anyway, that makes it difficult to have hard-coded arguments.
- The scripts `arandr` generates are hardly readable because it just dumps all agruments. I like having one line per `--output`, and it's a bit annoying to manually maintain that.
- `xrandr` doesn't deactivate the outputs by default, I could have a list of all possible outputs (xrandr ignores orders to deactivate non-existent screens), but that seems to be tedious and fragile (what if at some time `DP-42-2` appears)? 

## Description
The python script is quite simple.
First, it parses the xrandr output and structures it into classes `Screen`, `Mode` and `FPS`.
Then it assembles a `xrandr`-command to place the active screens next to each other.
The order of screens can be passed as arguments, regex is supported.
Screens which names cannot be matched to an command line argument will be deactivated.
All screens which are listed by xrandr as "disconnected" will be turned off.
The xrandr command will be run and printed nicely formatted.
If a screen supports multiple modes (resolution, frequency), the best (highest) one is picked.

## Example
```
pyrandr eDP-1                 # activate eDP-1 only
pyrandr eDP-1 DP-2-3          # place DP-2-3 right of eDP-1
pyrandr DP-3-3 eDP-1 DP-2-3   # place eDP-1 in the middle of DP-3-3 and DP-2-3
pyrandr eDP-1 DP-.*-3         # don't care if it's DP-2-3, DP-3-3 or DP-foobar-3.
```

```
% ./pyrandr.py 'DP-.*-2' 'DP-.*-3' eDP-1
xrandr\
--output HDMI-1 --off\
--output DP-1 --off\
--output DP-2 --off\
--output DP-3 --off\
--output DP-4 --off\
--output DP-3-1 --off\
--output DP-3-2 --mode 1920x1080 --pos 0x0 --rotate normal\
--output DP-3-3 --mode 1920x1080 --pos 1920x0 --rotate normal\
--output eDP-1 --mode 3072x1920 --pos 3840x0 --rotate normal
```

## Limitations, possible extensions
As this is currently tied to my specific use case, I consider this to be feature-complete.
Maybe in future if the use case becomes more general, following features might be nice:

- dry run: only print the xrandr command but don't actually run it
- quite mode: don't print the xrandr command
- verbose mode: list all screens and modes
- support y-offsets or align screens at bottom rather than at top
- support picking other modes
- this list is not complete.
