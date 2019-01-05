./webserver.py &
firefox -url http://superuser.com &
xdotool search --sync --onlyvisible --class "Firefox" windowactivate key F11