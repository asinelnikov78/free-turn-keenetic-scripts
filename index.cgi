#!/bin/sh
printf "Content-type: text/html; charset=utf-8\r\n\r\n"

# Принудительно фиксируем рабочую папку веб-сервера
cd /opt/share/www/cgi-bin 2>/dev/null

# Жесткие абсолютные пути, которые веб-сервер видит идеально
WEB_STATUS_FILE="/opt/share/www/cgi-bin/mon_web_status.txt"
TEMPLATE_FILE="/opt/share/www/cgi-bin/template.html"
IF_LOG="/opt/share/www/cgi-bin/vk-turn-panel.log"
MONITOR_SCRIPT="/opt/etc/init.d/S99vk-turn-panel"

parse_post() {
    echo "$1" | sed 's/+/ /g;s/%\([0-9A-F][0-9A-F]\)/\\x\1/g' | xargs -0 printf "%b" 2>/dev/null
}

# Обработка сохранения интерактивной формы POST (Передаем данные нашему root-скрипту)
if [ "$REQUEST_METHOD" = "POST" ]; then
    read -r POST_DATA
    val_listen=$(echo "$POST_DATA" | grep -o 'listen=[^&]*' | cut -d= -f2)
    val_peer=$(echo "$POST_DATA" | grep -o 'peer=[^&]*' | cut -d= -f2)
    val_streams=$(echo "$POST_DATA" | grep -o 'streams=[^&]*' | cut -d= -f2)
    val_browser=$(echo "$POST_DATA" | grep -o 'browser=[^&]*' | cut -d= -f2)
    val_profile=$(echo "$POST_DATA" | grep -o 'obf_profile=[^&]*' | cut -d= -f2)
    val_timing=$(echo "$POST_DATA" | grep -o 'obf_timing=[^&]*' | cut -d= -f2)
    val_key=$(echo "$POST_DATA" | grep -o 'obf_key=[^&]*' | cut -d= -f2)
    val_links=$(echo "$POST_DATA" | grep -o 'links=[^&]*' | cut -d= -f2)

    L_LISTEN=$(parse_post "$val_listen"); L_PEER=$(parse_post "$val_peer")
    L_STREAMS=$(parse_post "$val_streams"); L_BROWSER=$(parse_post "$val_browser")
    L_PROFILE=$(parse_post "$val_profile"); L_TIMING=$(parse_post "$val_timing")
    L_KEY=$(parse_post "$val_key"); L_LINKS=$(parse_post "$val_links")

    $MONITOR_SCRIPT save_json "$L_LISTEN" "$L_PEER" "$L_STREAMS" "$L_BROWSER" "$L_PROFILE" "$L_TIMING" "$L_KEY" "$L_LINKS" >/dev/null 2>&1
    echo "<meta http-equiv='refresh' content='0;url=index.cgi?tab=vkturn'>"
    exit 0
fi

CURRENT_TAB="manage"
case "$QUERY_STRING" in
    *tab=vkturn*) CURRENT_TAB="vkturn" ;;
    *tab=info*)   CURRENT_TAB="info" ;;
esac

# Стартовые значения переменных телеметрии по умолчанию
L2TP_ST="down"; L2TP_TX="OFFLINE"; VK_ST="down"; VK_TX="СПИТ"; WG_ST="down"; WG_TX="ОТКЛЮЧЕН"
WG_LINK="—"; WG_CONN="—"; WG_STATE="—"; SYS_CPU="0"; SYS_RAM="0"; SYS_VER="—"; SYS_UT="—"
MDM_OP="—"; MDM_TY="—"; MDM_SP="—"; MDM_SQ="—"; MDM_IP="—"; WEB_LOGS="Ожидание данных..."
VK_BIN="/opt/etc/vk-turn/vk-turn"; VK_LISTEN="—"; VK_PEER="—"; VK_STREAMS="—"; VK_BROWSER="—"; VK_PROFILE="—"; VK_TIMING="—"; VK_KEY="—"; VK_LINKS="—"

# НАДЁЖНЫЙ ИМПОРТ КЭША ЧЕРЕЗ АБСОЛЮТНЫЙ ПУТЬ ТОЧКИ
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

# ИСПРАВЛЕНО: ЧИСТЫЙ ПЕРЕВЕРНУТЫЙ СБОР С ОГРАНИЧЕНИЕМ СТРОК НА СТОРОНЕ ЯДРА (БЕЗ AWK/TAIL/SED)
if [ -f "$IF_LOG" ]; then
    WEB_LOGS=""
    log_count=0
    
    # Используем чистый внутренний reverse-парсер из успешного ТЕСТА 6
    while IFS= read -r log_line || [ -n "$log_line" ]; do
        [ -z "$log_line" ] && continue
        
        # Накапливаем строки в обратном порядке (свежие записи летят наверх)
        WEB_LOGS="${log_line}
${WEB_LOGS}"

        # Ограничитель: инкрементируем счетчик строк силами самого ядра sh
        log_count=$((log_count + 1))
        [ "$log_count" -ge 100 ] && break
    done < "$IF_LOG"
else
    WEB_LOGS="Лог-файл vk-turn-panel.log еще не создан автоматикой."
fi

# Системные страховки путей на случай самого первого старта автоматики
[ -z "$PIDFILE" ] && PIDFILE="/var/run/vk-turn-panel.pid"
[ -z "$L2TP_SYS_NAME" ] && L2TP_SYS_NAME="L2TP0"
[ -z "$WG_SYS_NAME" ] && WG_SYS_NAME="Wireguard0"

# Обработчик интерактивных кнопок действий пульта управления ( GET запросы )
if echo "$QUERY_STRING" | grep -q "action="; then
    case "$QUERY_STRING" in
        *action=start*)   $MONITOR_SCRIPT start >/dev/null 2>&1 ;;
        *action=stop*)    $MONITOR_SCRIPT stop >/dev/null 2>&1 ;;
        *action=restart*) $MONITOR_SCRIPT restart >/dev/null 2>&1 ;;
        *action=clearlog*) echo "$(date '+%Y-%m-%d %H:%M:%S') - Лог очищен" > "$IF_LOG" ;;
        *action=reboot*)  /opt/sbin/ndmq -p "system reboot" >/dev/null 2>&1 ;;
        *action=recon*)   /opt/sbin/ndmq -p "interface ${L2TP_SYS_NAME} down" >/dev/null 2>&1; sleep 1; /opt/sbin/ndmq -p "interface ${L2TP_SYS_NAME} up" >/dev/null 2>&1 ;;
    esac
    [ "$CURRENT_TAB" != "manage" ] && echo "<meta http-equiv='refresh' content='0;url=index.cgi?tab=${CURRENT_TAB}'>" || echo "<meta http-equiv='refresh' content='0;url=index.cgi'>"
    exit 0
fi

# Проверка активности фонового root демона по динамическому PID файлу из кэша статусов
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
    MON_ST="up"; MON_TX="АКТИВЕН"; MON_REFRESH=1
else
    MON_ST="down"; MON_TX="ВЫКЛЮЧЕН"; MON_REFRESH=0
fi

META_REFRESH=""
if [ "$MON_REFRESH" = "1" ] && [ "$CURRENT_TAB" != "vkturn" ]; then 
    if [ "$CURRENT_TAB" != "manage" ]; then META_REFRESH="<meta http-equiv='refresh' content='5;url=index.cgi?tab=${CURRENT_TAB}'>"; else META_REFRESH="<meta http-equiv='refresh' content='5;url=index.cgi'>"; fi
fi

TAB_NAV="<a href='index.cgi' class='tab-link $( [ "$CURRENT_TAB" = "manage" ] && echo "active" )'>🎛️ УПРАВЛЕНИЕ</a> <a href='index.cgi?tab=vkturn' class='tab-link $( [ "$CURRENT_TAB" = "vkturn" ] && echo "active" )'>🔄 VK TURN</a> <a href='index.cgi?tab=info' class='tab-link $( [ "$CURRENT_TAB" = "info" ] && echo "active" )'>📊 ИНФОРМАЦИЯ</a>"

DISP_MAN="none"; DISP_VKT="none"; DISP_INF="none"
[ "$CURRENT_TAB" = "manage" ] && DISP_MAN="block"; [ "$CURRENT_TAB" = "vkturn" ] && DISP_VKT="block"; [ "$CURRENT_TAB" = "info" ] && DISP_INF="block"

# Сквозная подстановка динамических переменных в файл HTML-шаблона
if [ -f "$TEMPLATE_FILE" ]; then
    while IFS= read -r line || [ -n "$line" ]; do
        line="${line//%META_REFRESH%/$META_REFRESH}"
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
        line="${line//%VK_BIN%/$VK_BIN}"
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
        echo "$line"
    done < "$TEMPLATE_FILE"
else
    echo "⚠️ Ошибка: Файл HTML-шаблона template.html не найден по абсолютному пути $TEMPLATE_FILE!"
fi
