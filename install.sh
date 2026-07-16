#!/bin/sh

# ==============================================================================
# Интерактивный установщик комплекса мониторинга из отдельных файлов GitHub
# ==============================================================================

# ⚠️ ВПИШИТЕ СЮДА ВАШИ ДАННЫЕ GITHUB, ЧТОБЫ СКРИПТ ЗНАЛ ОТКУДА СКАЧИВАТЬ:
GITHUB_USER="ВАШ_НИК_НА_GITHUB"
REPO_NAME="keenetic-l2tp-monitor"
BRANCH="master" # или main, смотря как названа ветка в гитхабе

BASE_URL="https://githubusercontent.com{GITHUB_USER}/${REPO_NAME}/${BRANCH}"

echo "----------------------------------------"
echo "🚀 Добро пожаловать в инсталлятор L2TP Монитора!"
echo "----------------------------------------"

# Интерактивный опрос номера порта
DEFAULT_PORT="17112"
printf "🌐 Введите порт для веб-панели [по умолчанию %s]: " "$DEFAULT_PORT"
read -r USER_PORT

# Если пользователь просто нажал Enter, оставляем порт по умолчанию
if [ -z "$USER_PORT" ]; then
    WEB_PORT="$DEFAULT_PORT"
else
    WEB_PORT="$USER_PORT"
fi

echo "✅ Выбран порт для веб-панели: $WEB_PORT"
echo ""

# Шаг 1: Установка пакетов
echo "📦 Шаг 1: Установка lighttpd и curl..."
opkg update
opkg install lighttpd curl
echo "✅ Базовые пакеты установлены."
echo ""

# Шаг 2: Подготовка папок
echo "📁 Шаг 2: Создание системных директорий..."
mkdir -p /opt/etc/VK-Turn/logs
mkdir -p /opt/etc/VK-Turn/run
mkdir -p /opt/share/www/cgi-bin
mkdir -p /opt/var
echo "✅ Структура папок готова."
echo ""

# Шаг 3: Настройка lighttpd под root и смена веб-порта
echo "⚙️ Шаг 3: Конфигурация веб-сервера lighttpd..."
LIGHT_CONF="/opt/etc/lighttpd/lighttpd.conf"
if [ -f "$LIGHT_CONF" ]; then
    # Очищаем от ограничений прав пользователя nobody
    sed -i '/server.username/d' "$LIGHT_CONF"
    sed -i '/server.groupname/d' "$LIGHT_CONF"
    
    # Меняем порт веб-сервера lighttpd на выбранный пользователем
    if grep -q "server.port" "$LIGHT_CONF"; then
        sed -i "s/server.port.*/server.port = $WEB_PORT/" "$LIGHT_CONF"
    else
        echo "server.port = $WEB_PORT" >> "$LIGHT_CONF"
    fi
    echo "✅ Файл lighttpd.conf успешно настроен на порт $WEB_PORT."
else
    echo "⚠️ Внимание: Конфиг lighttpd не найден, пропустили шаг настройки порта."
fi
echo ""

# Шаг 4: Скачивание скрипта монитора из отдельного файла на GitHub
echo "📥 Шаг 4: Скачивание фонового демона S99l2tp-monitor..."
curl -sL "${BASE_URL}/S99l2tp-monitor" -o /opt/etc/init.d/S99l2tp-monitor
if [ $? -eq 0 ] && [ -s /opt/etc/init.d/S99l2tp-monitor ]; then
    echo "✅ Скрипт автоматики успешно скачан."
else
    echo "❌ Ошибка скачивания S99l2tp-monitor! Проверьте имя файла в репозитории."
    exit 1
fi
echo ""

# Шаг 5: Скачивание веб-панели из отдельного файла на GitHub
echo "🖥️ Шаг 5: Скачивание скрипта веб-панели index.cgi..."
curl -sL "${BASE_URL}/index.cgi" -o /opt/share/www/cgi-bin/index.cgi
if [ $? -eq 0 ] && [ -s /opt/share/www/cgi-bin/index.cgi ]; then
    echo "✅ Веб-панель успешно скачана."
else
    echo "❌ Ошибка скачивания index.cgi! Проверьте имя файла в репозитории."
    exit 1
fi
echo ""

# Шаг 6: Очистка строк и применение Unix-прав
echo "🔒 Шаг 6: Финальная обработка файлов и выставление прав..."
sed -i 's/\r$//' /opt/etc/init.d/S99l2tp-monitor
sed -i 's/\r$//' /opt/share/www/cgi-bin/index.cgi

chmod +x /opt/etc/init.d/S99l2tp-monitor
chmod +x /opt/share/www/cgi-bin/index.cgi
echo "✅ Права на запуск успешно выданы."
echo ""

# Шаг 7: Запуск комплекса
echo "🔄 Шаг 7: Перезапуск системных служб..."
/opt/etc/init.d/S80lighttpd restart
/opt/etc/init.d/S99l2tp-monitor restart
echo ""
echo "----------------------------------------"
echo "🎉 Установка полностью завершена!"
echo "👉 Ваша веб-панель доступна по адресу: http://192.168.2.1:$WEB_PORT"
echo "----------------------------------------"
