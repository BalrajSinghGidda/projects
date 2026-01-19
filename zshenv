# Environment variables
. "/nix/store/fpn98v3hrk913r6qsxzb56vvffrvyiy8-hm-session-vars.sh/etc/profile.d/hm-session-vars.sh"

# Only source this once
if [[ -z "$__HM_ZSH_SESS_VARS_SOURCED" ]]; then
  export __HM_ZSH_SESS_VARS_SOURCED=1
  
fi

ZSH="/nix/store/jgvwrvz5jrg23cn81nn5p0m4yjlxrb66-oh-my-zsh-2025-11-09/share/oh-my-zsh";
ZSH_CACHE_DIR="/home/balraj/.cache/oh-my-zsh";
