#!/bin/sh
printf "Content-type: text/html; charset=utf-8\r\n\r\n"

MONITOR_SCRIPT="/opt/etc/init.d/S99l2tp-monitor"
PIDFILE="/var/run/l2tp-monitor.pid"
WEB_STATUS_FILE="/opt/var/mon_web_status.txt"

if [ -n "$QUERY_STRING" ]; then
    case "$QUERY_STRING" in
        action=start)   $MONITOR_SCRIPT start >/dev/null 2>&1 ;;
        action=stop)    $MONITOR_SCRIPT stop >/dev/null 2>&1 ;;
        action=restart) $MONITOR_SCRIPT restart >/dev/null 2>&1 ;;
    esac
    echo "<meta http-equiv='refresh' content='0;url=index.cgi'>"
    exit 0
fi

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
    MON_ST="up"; MON_TX="АКТИВЕН"; MON_REFRESH=1
else
    MON_ST="down"; MON_TX="ВЫКЛЮЧЕН"; MON_REFRESH=0
fi

L2TP_ST="down"; L2TP_TX="OFFLINE"
VK_ST="down"; VK_TX="СПИТ"
WG_ST="down"; WG_TX="ОТКЛЮЧЕН"
WG_LINK="down"; WG_CONN="no"; WG_STATE="down"
WEB_LOGS="Ожидание первой выгрузки логов из системы..."

if [ -f "$WEB_STATUS_FILE" ]; then
    . "$WEB_STATUS_FILE"
    [ "$L2TP" = "up" ] && { L2TP_ST="up"; L2TP_TX="ONLINE"; }
    [ "$VK" = "up" ] && { VK_ST="up"; VK_TX="РАБОТАЕТ"; }
    [ "$WG" = "up" ] && { WG_ST="up"; WG_TX="ПОДНЯТ"; }
    
    [ -n "$WG_L" ] && WG_LINK="$WG_L"
    [ -n "$WG_C" ] && WG_CONN="$WG_C"
    [ -n "$WG_S" ] && WG_STATE="$WG_S"
fi

echo "<!DOCTYPE html><html lang='ru'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'>"
if [ "$MON_REFRESH" = "1" ]; then echo "<meta http-equiv='refresh' content='5;url=index.cgi'>"; fi
echo "<title>L2TP Monitor Panel</title><style>"
echo "body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #121214; color: #e1e1e6; margin: 0; padding: 20px; display: flex; justify-content: center; }"
echo ".container { width: 100%; max-width: 500px; background: #202024; padding: 25px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3); }"
echo "h2 { margin-top: 0; text-align: center; color: #fff; font-weight: 600; border-bottom: 1px solid #323238; padding-bottom: 15px; }"
echo ".status-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }"
echo ".status-card { background: #29292e; padding: 15px; border-radius: 8px; border: 1px solid #323238; display: flex; flex-direction: column; align-items: center; text-align: center; justify-content: center; min-height: 95px; }"
echo ".status-title { font-size: 12px; color: #a8a8b3; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }"
echo ".badge { font-weight: bold; font-size: 14px; padding: 4px 12px; border-radius: 20px; display: inline-block; }"
echo ".badge.up { background: rgba(4,211,97,0.1); color: #04d361; }"
echo ".badge.down { background: rgba(247,70,70,0.1); color: #f74646; }"
echo ".wg-tech-info { font-family: monospace; font-size: 11px; color: #797985; margin-top: 8px; text-align: left; width: 100%; max-width: 120px; border-top: 1px solid #383842; padding-top: 6px; line-height: 1.4; }"
echo ".wg-tech-info span { color: #cbe1e6; font-weight: bold; float: right; }"
echo ".btn-group { display: flex; gap: 10px; margin-top: 25px; }"
echo ".btn { flex: 1; padding: 12px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; transition: background 0.2s; font-size: 14px; text-decoration: none; text-align: center; }"
echo ".btn-start { background: #04d361; color: #000; }"
echo ".btn-start:hover { background: #02b351; }"
echo ".btn-stop { background: #f74646; color: #fff; }"
echo ".btn-stop:hover { background: #d63b3b; }"
echo ".btn-restart { background: #4e4e54; color: #fff; }"
echo ".btn-restart:hover { background: #3e3e44; }"
echo ".log-header { display: flex; justify-content: space-between; align-items: center; margin-top: 30px; margin-bottom: 10px; }"
echo ".log-title { font-size: 14px; color: #a8a8b3; font-weight: bold; text-transform: uppercase; }"
echo ".btn-refresh { font-size: 12px; color: #4da6ff; text-decoration: none; }"
echo "pre { background: #121214; padding: 15px; border-radius: 6px; border: 1px solid #323238; font-size: 11px; overflow-y: auto; overflow-x: hidden; white-space: pre-wrap; word-break: break-all; max-height: 180px; margin: 0; color: #8d8d99; font-family: monospace; box-sizing: border-box; width: 100%; }"
echo "</style></head><body><div class='container'><h2>L2TP Monitor Panel</h2>"

echo "<div class='status-grid'>"
echo "  <div class='status-card'><span class='status-title'>Монитор</span><span class='badge ${MON_ST}'>${MON_TX}</span></div>"
echo "  <div class='status-card'><span class='status-title'>Интерфейс L2TP</span><span class='badge ${L2TP_ST}'>${L2TP_TX}</span></div>"
echo "  <div class='status-card'><span class='status-title'>Сервис vk-turn</span><span class='badge ${VK_ST}'>${VK_TX}</span></div>"
echo "  <div class='status-card'><span class='status-title'>WireGuard Туннель</span><span class='badge ${WG_ST}'>${WG_TX}</span>"
echo "      <div class='wg-tech-info'>"
echo "          link: <span>${WG_LINK}</span><br>"
echo "          connected: <span>${WG_CONN}</span><br>"
echo "          state: <span>${WG_STATE}</span>"
echo "      </div>"
echo "  </div>"
echo "</div>"

echo "<div class='btn-group'>"
echo "  <a href='?action=start' class='btn btn-start'>Старт</a>"
echo "  <a href='?action=stop' class='btn btn-stop'>Стоп</a>"
echo "  <a href='?action=restart' class='btn btn-restart'>Рестарт</a>"
echo "</div>"

echo "<div class='log-header'>"
echo "  <span class='log-title'>Последние логи</span>"
echo "  <a href='index.cgi' class='btn-refresh'>Обновить статус</a>"
echo "</div>"

echo "<pre>${WEB_LOGS}</pre>"
echo "</div></body></html>"
