#!/usr/bin/env fish
# BUG FIX #12: Original: 'if _reload' tried to execute $_reload as a command.
# Fixed: 'if test $_reload = true' correctly tests the variable's value.
# The original would always throw a "command not found: false" error on reload.

set -l _reload false

# Ensure config directory exists
if ! test -d $argv[1]
    mkdir -p $argv[1]
end

# Ensure hypr-vars exists (user can override Hyprland variables here)
if ! test -f $argv[1]/hypr-vars.conf
    touch $argv[1]/hypr-vars.conf
    set _reload true
end

# Ensure hypr-user exists (user can add custom Hyprland config here)
if ! test -f $argv[1]/hypr-user.conf
    touch $argv[1]/hypr-user.conf
    set _reload true
end

# Reload as needed — but only when actually inside a Hyprland session
if test $_reload = true
    if set -q HYPRLAND_INSTANCE_SIGNATURE
        hyprctl reload 2>/dev/null
    end
end
