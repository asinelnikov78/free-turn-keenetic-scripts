// ===== ОБНОВЛЕНИЕ ДАННЫХ =====
(function() {
    let isFirstLoad = true;

    function updateData() {
        fetch('/cgi-bin/index.cgi?ajax=1')
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');

                const newLogs = doc.querySelector('pre')?.innerHTML;
                const oldLogs = document.querySelector('pre');
                if (newLogs && oldLogs && oldLogs.innerHTML !== newLogs) {
                    oldLogs.innerHTML = newLogs;
                }

                const newBadges = doc.querySelectorAll('.badge');
                const oldBadges = document.querySelectorAll('.badge');
                newBadges.forEach((newBadge, index) => {
                    if (oldBadges[index] && oldBadges[index].innerHTML !== newBadge.innerHTML) {
                        oldBadges[index].innerHTML = newBadge.innerHTML;
                        oldBadges[index].className = newBadge.className;
                    }
                });

                const newWg = doc.querySelector('.wg-tech-info');
                const oldWg = document.querySelector('.wg-tech-info');
                if (newWg && oldWg && oldWg.innerHTML !== newWg.innerHTML) {
                    oldWg.innerHTML = newWg.innerHTML;
                }

                const newInfoRows = doc.querySelectorAll('.info-block .info-row span');
                const oldInfoRows = document.querySelectorAll('.info-block .info-row span');
                newInfoRows.forEach((newSpan, index) => {
                    if (oldInfoRows[index] && oldInfoRows[index].innerHTML !== newSpan.innerHTML) {
                        oldInfoRows[index].innerHTML = newSpan.innerHTML;
                    }
                });

                const newProgress = doc.querySelectorAll('.progress-fill');
                const oldProgress = document.querySelectorAll('.progress-fill');
                newProgress.forEach((newBar, index) => {
                    if (oldProgress[index] && oldProgress[index].style.width !== newBar.style.width) {
                        oldProgress[index].style.width = newBar.style.width;
                    }
                });

                if (!isFirstLoad) {
                    document.querySelector('.container')?.style.setProperty('--flash', '0.3s');
                }
                isFirstLoad = false;
            })
            .catch(err => console.log('Update error:', err));
    }

    // Делаем updateData доступной глобально
    window.updateData = updateData;

    setInterval(updateData, 1000);
    setTimeout(updateData, 100);
})();

// ===== ВКЛАДКИ И КНОПКИ (после загрузки DOM) =====
document.addEventListener('DOMContentLoaded', function() {
    // --- Вкладки ---
    var urlParams = new URLSearchParams(window.location.search);
    var tab = urlParams.get('tab') || 'manage';
    
    document.querySelectorAll('#tab-manage, #tab-vkturn, #tab-info').forEach(function(el) {
        el.style.display = 'none';
    });
    document.getElementById('tab-' + tab).style.display = 'block';
    
    document.querySelectorAll('.tab-link').forEach(function(el) {
        el.classList.remove('active');
        if (el.getAttribute('href').includes('tab=' + tab)) {
            el.classList.add('active');
        }
    });

    // --- Подсветка вкладок при клике ---
    document.querySelectorAll('.tab-link').forEach(function(tabLink) {
        tabLink.addEventListener('click', function(e) {
            document.querySelectorAll('.tab-link').forEach(function(el) {
                el.classList.remove('active');
            });
            this.classList.add('active');
        });
    });

    // --- Кнопки СТАРТ/СТОП (без перезагрузки) ---
    document.querySelectorAll('.btn-start, .btn-stop, .btn-blue, .btn-refresh').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.href;
            if (this.classList.contains('btn-stop') && this.textContent.includes('Перезагрузка')) {
                if (!confirm('Точно перезагрузить роутер?')) return;
            }
            fetch(url)
                .then(function() {
                    setTimeout(window.updateData, 500);
                })
                .catch(function(err) {
                    console.log('Click error:', err);
                });
        });
    });

    // --- Кнопка СОХРАНИТЬ (через JS) ---
    document.querySelector('button[type="submit"]')?.addEventListener('click', function(e) {
        e.preventDefault();
        
        const form = this.closest('form');
        const inputs = form.querySelectorAll('input, select, textarea');
        let params = [];
        inputs.forEach(function(input) {
            if (input.name) {
                params.push(encodeURIComponent(input.name) + '=' + encodeURIComponent(input.value));
            }
        });
        const queryString = params.join('&');
        console.log("Saving:", queryString);
        
        fetch('/cgi-bin/index.cgi?action=save&' + queryString)
            .then(function() {
                setTimeout(window.updateData, 500);
            })
            .catch(function(err) {
                console.log('Save error:', err);
            });
    });
});