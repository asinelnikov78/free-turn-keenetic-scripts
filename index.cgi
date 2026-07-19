#!/bin/sh
echo "$(date) - QUERY_STRING=$QUERY_STRING" >> /tmp/debug.log
printf "Content-type: text/html; charset=utf-8\r\n\r\n"
cd /opt/share/www/cgi-bin 2>/dev/null

WEB_STATUS_FILE="/opt/share/www/cgi-bin/mon_web_status.txt"
TEMPLATE_FILE="/opt/share/www/cgi-bin/template.html"
IF_LOG="/opt/share/www/cgi-bin/vk-turn-panel.log"

CURRENT_TAB="manage"
case "$QUERY_STRING" in
    *tab=vkturn*) CURRENT_TAB="vkturn" ;;
    *tab=info*)   CURRENT_TAB="info" ;;
esac

L2TP_ST="down"; L2TP_TX="OFFLINE"; VK_ST="down"; VK_TX="СПИТ"; WG_ST="down"; WG_TX="ОТКЛЮЧЕН"
WG_LINK="—"; WG_CONN="—"; WG_STATE="—"; SYS_CPU="0"; SYS_RAM="0"; SYS_VER="—"; SYS_UT="—"
MDM_OP="—"; MDM_TY="—"; MDM_SP="—"; MDM_SQ="—"; MDM_IP="—"
VK_BIN="/opt/etc/vk-turn/vk-turn"; VK_LISTEN="—"; VK_PEER="—"; VK_STREAMS="—"; VK_BROWSER="—"; VK_PROFILE="—"; VK_TIMING="—"; VK_KEY="—"; VK_LINKS="—"

if [ -f "$WEB_STATUS_FILE" ]; then
    . "$WEB_STATUS_FILE"
    [ "$L2TP" = "up" ] && { L2TP_ST="up"; L2TP_TX="ONLINE"; }
    [ "$VK" = "up" ]   && { VK_ST="up";   VK_TX="РАБОТАЕТ"; }
    [ "$WG" = "up" ]   && { WG_ST="up";   WG_TX="ПОДНЯТ"; }
    [ -n "$WG_L" ] && WG_LINK="$WG_L"
    [ -n "$WG_C" ] && WG_CONN="$WG_C"
    [ -n "$WG_S" ] && WG_STATE="$WG_S"
    [ -n "$SYS_CPU" ] && SYS_CPU="$SYS_CPU"
    [ -n "$SYS_RAM" ] && SYS_RAM="$SYS_RAM"
    [ -n "$SYS_VER" ] && SYS_VER="$SYS_VER"
    [ -n "$SYS_UT" ] && SYS_UT="$SYS_UT"
    [ -n "$MDM_OP" ] && MDM_OP="$MDM_OP"
    [ -n "$MDM_TY" ] && MDM_TY="$MDM_TY"
    [ -n "$MDM_SP" ] && MDM_SP="$MDM_SP"
    [ -n "$MDM_SQ" ] && MDM_SQ="$MDM_SQ"
    [ -n "$MDM_IP" ] && MDM_IP="$MDM_IP"
    [ -n "$VK_BIN" ] && VK_BIN="$VK_BIN"
    [ -n "$VK_LISTEN" ] && VK_LISTEN="$VK_LISTEN"
    [ -n "$VK_PEER" ] && VK_PEER="$VK_PEER"
    [ -n "$VK_STREAMS" ] && VK_STREAMS="$VK_STREAMS"
    [ -n "$VK_BROWSER" ] && VK_BROWSER="$VK_BROWSER"
    [ -n "$VK_PROFILE" ] && VK_PROFILE="$VK_PROFILE"
    [ -n "$VK_TIMING" ] && VK_TIMING="$VK_TIMING"
    [ -n "$VK_KEY" ] && VK_KEY="$VK_KEY"
    [ -n "$VK_LINKS" ] && VK_LINKS="$VK_LINKS"
    PIDFILE="$PID_FILE"
    L2TP_SYS_NAME="$L2TP_NAME"
    WG_SYS_NAME="$WG_NAME"
fi

if [ -f "$IF_LOG" ]; then
    WEB_LOGS=""
    log_count=0
    while IFS= read -r log_line || [ -n "$log_line" ]; do
        [ -z "$log_line" ] && continue
        WEB_LOGS="${log_line}
${WEB_LOGS}"
        log_count=$((log_count + 1))
        [ "$log_count" -ge 100 ] && break
    done < "$IF_LOG"
else
    WEB_LOGS="Лог-файл vk-turn-panel.log еще не создан автоматикой."
fi

[ -z "$PIDFILE" ] && PIDFILE="/var/run/vk-turn-panel.pid"
[ -z "$L2TP_SYS_NAME" ] && L2TP_SYS_NAME="L2TP0"
[ -z "$WG_SYS_NAME" ] && WG_SYS_NAME="Wireguard0"

case "$QUERY_STRING" in
    *action=start*)
        > /opt/share/www/cgi-bin/cmd_start
        chmod 666 /opt/share/www/cgi-bin/cmd_start
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 🟢 Команда START" >> "$IF_LOG"
        echo "<meta http-equiv='refresh' content='0;url=index.cgi'>"
        exit 0
        ;;
    *action=stop*)
        > /opt/share/www/cgi-bin/cmd_stop
        chmod 666 /opt/share/www/cgi-bin/cmd_stop
        echo "$(date '+%Y-%m-%d %H:%M:%S') - 🔴 Команда STOP" >> "$IF_LOG"
        echo "<meta http-equiv='refresh' content='0;url=index.cgi'>"
        exit 0
        ;;
	*action=save*)
		#LISTEN=""
		# PEER=""
		# STREAMS=""
		# BROWSER=""
		# PROFILE=""
		# TIMING=""
		# KEY=""
		# LINKS=""

		# IFS='&'
		# for PAIR in $QUERY_STRING; do
			# case "$PAIR" in
				# listen=*) LISTEN="${PAIR#listen=}" ;;
				# peer=*) PEER="${PAIR#peer=}" ;;
				# streams=*) STREAMS="${PAIR#streams=}" ;;
				# browser=*) BROWSER="${PAIR#browser=}" ;;
				# obf_profile=*) PROFILE="${PAIR#obf_profile=}" ;;
				# obf_timing=*) TIMING="${PAIR#obf_timing=}" ;;
# #				case "$TIMING" in
# #					*ms) ;;
# #					*) TIMING="${TIMING}ms" ;;
# #				esac
				# obf_key=*) KEY="${PAIR#obf_key=}" ;;
				# links=*) LINKS="${PAIR#links=}" ;;
			# esac
		# done
#		Q_STRING="ave&listen=127.0.0.19000&peer=wildkid.netcraze.pro"
#		echo "DEBUG: SENDING to save_json: Q_STRING = $Q_STRING" >> /tmp/debug.log   
#		echo "DEBUG: ACTION_STRING = $QUERY_STRING" >> /tmp/debug.log
#		LISTEN=$(echo "$Q_STRING" | grep -o 'listen=[^&]*')
#		LISTEN=$(echo "$QUERY_STRING" | grep -o 'listen=[^&]*' | cut -d= -f2 | head -1)
#		PEER=$(echo "$QUERY_STRING" | grep -o 'peer=[^&]*' | cut -d= -f2 | head -1)
#		STREAMS=$(echo "$QUERY_STRING" | grep -o 'streams=[^&]*' | cut -d= -f2 | head -1)
#		BROWSER=$(echo "$QUERY_STRING" | grep -o 'browser=[^&]*' | cut -d= -f2 | head -1)
#		PROFILE=$(echo "$QUERY_STRING" | grep -o 'obf_profile=[^&]*' | cut -d= -f2 | head -1)
#		TIMING=$(echo "$QUERY_STRING" | grep -o 'obf_timing=[^&]*' | cut -d= -f2 | head -1)
#		KEY=$(echo "$QUERY_STRING" | grep -o 'obf_key=[^&]*' | cut -d= -f2 | head -1)
#		LINKS=$(echo "$QUERY_STRING" | grep -o 'links=[^&]*' | cut -d= -f2 | head -1)
 #   echo "DEBUG: SENDING to save_json: LISTEN = $LISTEN" >> /tmp/debug.log   
#	echo "DEBUG: SENDING to save_json: LISTEN = $LISTEN" >> /tmp/debug.log 
	# echo "DEBUG: SENDING to save_json: LISTEN=$LISTEN PEER=$PEER STREAMS=$STREAMS BROWSER=$BROWSER PROFILE=$PROFILE TIMING=$TIMING KEY=$KEY LINKS=$LINKS" >> /tmp/debug.log
		# /opt/etc/init.d/S99vk-turn-panel save_json "$LISTEN" "$PEER" "$STREAMS" "$BROWSER" "$PROFILE" "$TIMING" "$KEY" "$LINKS"
#    echo "DEBUG: CALLING save_json with STREAMS=$STREAMS" >> /tmp/debug.log
#		echo "DEBUG: STREAMS=$STREAMS" >> /tmp/debug.log
#		echo "OK"
        # Записываем QUERY_STRING в файл
        echo "$QUERY_STRING" > /opt/share/www/cgi-bin/cmd_query
        chmod 666 /opt/share/www/cgi-bin/cmd_query
        
        echo "<meta http-equiv='refresh' content='0;url=index.cgi?tab=vkturn&saved=1'>"

		exit 0
		;;
esac

MON_REFRESH=1
if [ -f "$WEB_STATUS_FILE" ]; then
    . "$WEB_STATUS_FILE"
    if [ "$MONITOR_ENABLED" = "1" ]; then
        MON_ST="up"; MON_TX="ВКЛЮЧЕН"
    else
        MON_ST="down"; MON_TX="ВЫКЛЮЧЕН"
    fi
else
    MON_ST="down"; MON_TX="ВЫКЛЮЧЕН"
fi

TAB_NAV="<a href='index.cgi?tab=manage' class='tab-link $( [ "$CURRENT_TAB" = "manage" ] && echo "active" )'>🎛️ УПРАВЛЕНИЕ</a> <a href='index.cgi?tab=vkturn' class='tab-link $( [ "$CURRENT_TAB" = "vkturn" ] && echo "active" )'>🔄 VK TURN</a> <a href='index.cgi?tab=info' class='tab-link $( [ "$CURRENT_TAB" = "info" ] && echo "active" )'>📊 ИНФОРМАЦИЯ</a>"

DISP_MAN="none"; DISP_VKT="none"; DISP_INF="none"
[ "$CURRENT_TAB" = "manage" ] && DISP_MAN="block"
[ "$CURRENT_TAB" = "vkturn" ] && DISP_VKT="block"
[ "$CURRENT_TAB" = "info" ] && DISP_INF="block"

if [ -f "$TEMPLATE_FILE" ]; then
    VK_PROFILE_NONE_SELECTED=""; VK_PROFILE_RTPOPUS_SELECTED=""; VK_PROFILE_RTPOPUS2_SELECTED=""; VK_PROFILE_RTPOPUS3_SELECTED=""
    case "$VK_PROFILE" in
        "none") VK_PROFILE_NONE_SELECTED="selected" ;;
        "rtpopus") VK_PROFILE_RTPOPUS_SELECTED="selected" ;;
        "rtpopus2") VK_PROFILE_RTPOPUS2_SELECTED="selected" ;;
        "rtpopus3") VK_PROFILE_RTPOPUS3_SELECTED="selected" ;;
    esac
    VK_BROWSER_CHROME_SELECTED=""; VK_BROWSER_FIREFOX_SELECTED=""; VK_BROWSER_SAFARI_SELECTED=""
    case "$VK_BROWSER" in
        "chrome") VK_BROWSER_CHROME_SELECTED="selected" ;;
        "firefox") VK_BROWSER_FIREFOX_SELECTED="selected" ;;
        "safari") VK_BROWSER_SAFARI_SELECTED="selected" ;;
    esac
    while IFS= read -r line || [ -n "$line" ]; do
        line="${line//%TAB_NAVIGATION%/$TAB_NAV}"
        line="${line//%CURRENT_TAB%/$CURRENT_TAB}"
        line="${line//%CSS_MANAGE%/$DISP_MAN}"
        line="${line//%CSS_VKTURN%/$DISP_VKT}"
        line="${line//%CSS_INFO%/$DISP_INF}"
        line="${line//%MON_ST%/$MON_ST}"
        line="${line//%MON_TX%/$MON_TX}"
        line="${line//%L2TP_ST%/$L2TP_ST}"
        line="${line//%L2TP_TX%/$L2TP_TX}"
        line="${line//%VK_ST%/$VK_ST}"
        line="${line//%VK_TX%/$VK_TX}"
        line="${line//%WG_ST%/$WG_ST}"
        line="${line//%WG_TX%/$WG_TX}"
        line="${line//%WG_LINK%/$WG_LINK}"
        line="${line//%WG_CONN%/$WG_CONN}"
        line="${line//%WG_STATE%/$WG_STATE}"
        line="${line//%VK_LISTEN%/$VK_LISTEN}"
        line="${line//%VK_PEER%/$VK_PEER}"
        line="${line//%VK_STREAMS%/$VK_STREAMS}"
        line="${line//%VK_PROFILE%/$VK_PROFILE}"
        line="${line//%VK_TIMING%/$VK_TIMING}"
        line="${line//%VK_BROWSER%/$VK_BROWSER}"
        line="${line//%VK_KEY%/$VK_KEY}"
        line="${line//%VK_LINKS%/$VK_LINKS}"
        line="${line//%SYS_VER%/$SYS_VER}"
        line="${line//%SYS_UT%/$SYS_UT}"
        line="${line//%SYS_CPU%/$SYS_CPU}"
        line="${line//%SYS_RAM%/$SYS_RAM}"
        line="${line//%MDM_OP%/$MDM_OP}"
        line="${line//%MDM_TY%/$MDM_TY}"
        line="${line//%MDM_SP%/$MDM_SP}"
        line="${line//%MDM_SQ%/$MDM_SQ}"
        line="${line//%MDM_IP%/$MDM_IP}"
        line="${line//%WEB_LOGS%/$WEB_LOGS}"
        line="${line//%VK_PROFILE_NONE_SELECTED%/$VK_PROFILE_NONE_SELECTED}"
        line="${line//%VK_PROFILE_RTPOPUS_SELECTED%/$VK_PROFILE_RTPOPUS_SELECTED}"
        line="${line//%VK_PROFILE_RTPOPUS2_SELECTED%/$VK_PROFILE_RTPOPUS2_SELECTED}"
        line="${line//%VK_PROFILE_RTPOPUS3_SELECTED%/$VK_PROFILE_RTPOPUS3_SELECTED}"
        line="${line//%VK_BROWSER_CHROME_SELECTED%/$VK_BROWSER_CHROME_SELECTED}"
        line="${line//%VK_BROWSER_FIREFOX_SELECTED%/$VK_BROWSER_FIREFOX_SELECTED}"
        line="${line//%VK_BROWSER_SAFARI_SELECTED%/$VK_BROWSER_SAFARI_SELECTED}"
        echo "$line"
    done < "$TEMPLATE_FILE"
else
    echo "⚠️ Ошибка: Файл HTML-шаблона template.html не найден!"
fi
