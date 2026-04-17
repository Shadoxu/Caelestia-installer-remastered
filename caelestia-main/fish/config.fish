# =============================================================================
# Caelestia — Fish Shell Configuration
# BUG FIX: Added 'command -v' guards around optional tools (direnv, zoxide)
# so the fish config doesn't silently fail if they're not installed yet.
# BUG FIX: user-config.fish source path corrected to use $XDG_CONFIG_HOME
# so it respects the user's actual config dir (not hardcoded ~/.config).
# =============================================================================

if status is-interactive
    # ── Starship prompt ──
    if command -q starship
        starship init fish | source
    end

    # ── Direnv integration (isolated dev environments) ──
    if command -q direnv
        direnv hook fish | source
    end

    # ── Zoxide (smarter cd) ──
    if command -q zoxide
        zoxide init fish --cmd cd | source
    end

    # ── Better ls via eza ──
    if command -q eza
        alias ls='eza --icons --group-directories-first -1'
    end

    # ── Git abbreviations ──
    abbr lg  'lazygit'
    abbr gd  'git diff'
    abbr ga  'git add .'
    abbr gc  'git commit -am'
    abbr gl  'git log'
    abbr gs  'git status'
    abbr gst 'git stash'
    abbr gsp 'git stash pop'
    abbr gp  'git push'
    abbr gpl 'git pull'
    abbr gsw 'git switch'
    abbr gsm 'git switch main'
    abbr gb  'git branch'
    abbr gbd 'git branch -d'
    abbr gco 'git checkout'
    abbr gsh 'git show'

    # ── ls aliases ──
    abbr l   'ls'
    abbr ll  'ls -l'
    abbr la  'ls -a'
    abbr lla 'ls -la'

    # ── Caelestia terminal color sequences ──
    # Applies the color scheme to this terminal instance
    set -l _seq_file (
        test -n "$XDG_STATE_HOME"
        and echo "$XDG_STATE_HOME/caelestia/sequences.txt"
        or echo "$HOME/.local/state/caelestia/sequences.txt"
    )
    cat $_seq_file 2>/dev/null

    # ── foot prompt marker (enables jump-to-prompt in foot terminal) ──
    function mark_prompt_start --on-event fish_prompt
        echo -en "\e]133;A\e\\"
    end

    # ── User config extension ──
    # Create ~/.config/caelestia/user-config.fish to add your own settings.
    # A template is provided in caelestia-user-templates/user-config.fish.
    set -l _user_conf (
        test -n "$XDG_CONFIG_HOME"
        and echo "$XDG_CONFIG_HOME/caelestia/user-config.fish"
        or echo "$HOME/.config/caelestia/user-config.fish"
    )
    if test -f $_user_conf
        source $_user_conf
    end
end

# Caelestia PATH
export PATH="$HOME/.local/bin:$PATH"

# Caelestia PATH
export PATH="$HOME/.local/bin:$PATH"
